#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Items Scraper - Récupération des données de la Database Items Eden
Permet de rechercher et extraire les informations des items
"""

import time
import json
import html
import re
import urllib.parse
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from .logging_manager import get_logger, LOGGER_EDEN


class ItemsScraper:
    """
    Scraper pour la Database Items Eden-DAOC
    Permet de rechercher des items et extraire leurs informations
    """
    
    # Mapping des royaumes
    REALM_MAP = {
        "All": 0,
        "Albion": 1,
        "Midgard": 2,
        "Hibernia": 3
    }
    
    # Mapping des classes par royaume
    CLASS_MAP = {
        # Albion
        "Armsman": 2, "Mercenary": 11, "Paladin": 1, "Reaver": 19,
        "Cabalist": 13, "Necromancer": 12, "Occultist": 63, "Sorcerer": 8,
        "Theurgist": 5, "Wizard": 7, "Cleric": 6, "Friar": 10,
        "Heretic": 33, "Infiltrator": 9, "Minstrel": 4, "Scout": 3,
        # Hibernia
        "Blademaster": 43, "Champion": 45, "Hero": 44, "Valewalker": 56,
        "Vampiir": 58, "Animist": 55, "Eldritch": 40, "Enchanter": 41,
        "Mentalist": 42, "Bainshee": 39, "Bard": 48, "Druid": 47,
        "Warden": 46, "Nightshade": 49, "Ranger": 50,
        # Midgard
        "Berserker": 31, "Savage": 32, "Skald": 24, "Thane": 21,
        "Warrior": 22, "Valkyrie": 34, "Bonedancer": 30, "Runemaster": 29,
        "Spiritmaster": 27, "Warlock": 59, "Healer": 26, "Shaman": 28,
        "Hunter": 25, "Shadowblade": 23
    }
    
    # Mapping des slots
    SLOT_MAP = {
        # Jewelry
        "Cloak": "41-26", "Mythirian": "41-37", "Necklace": "41-29",
        "Jewel": "41-24", "Belt": "41-32", "Bracer": "41-33", "Ring": "41-35",
        # Armor
        "Helm": "0-21", "Arms": "0-28", "Gloves": "0-22",
        "Chest": "0-25", "Legs": "0-27", "Boots": "0-23",
        # Weapons
        "Crushing": "2-0", "Slashing": "3-0", "Thrust": "4-0",
        "Two Handed": "6-0", "Polearm": "7-0", "Crossbow": "10-0",
        "Flexible": "24-0", "Sword": "11-0", "Hammer": "12-0",
        "Axe": "13-0", "Spear": "14-0", "Thrown": "16-0",
        "Left Axe": "17-0", "Hand to Hand": "25-0", "Blade": "19-0",
        "Blunt": "20-0", "Piercing": "21-0", "Large Weapons": "22-0",
        "Celtic Spear": "23-0", "Scythe": "26-0", "Shield": "42-0",
        "Instrument": "45-0", "Staff": "8-0", "Longbow": "9-0",
        "Composite Bow": "15-0", "Recursive Bow": "18-0", "Short Bow": "5-0"
    }
    
    # Mapping des zones vers leurs abréviations
    ZONE_MAPPING = {
        "Passage of Conflict": "SH",  # Summoner's Hall
        "Summoner's Hall": "SH",
        "Sobekite Eternal": "SE",
        "Darkness Falls": "DF",
        "Caledonia": "Cale",
        "Thidranki": "Thid",
        "Abermenai": "Aber",
        "Camelot": "Camelot",
        "Jordheim": "Jordheim",
        "Tir na Nog": "TNN",
        "Oceanus Notos (Hibernia)": "Oceanus Hib",
        "Oceanus Notos (Albion)": "Oceanus Alb",
        "Oceanus Notos (Midgard)": "Oceanus Mid",
        "Oceanus Hesperos (Hibernia)": "Oceanus Hib",
        "Oceanus Hesperos (Albion)": "Oceanus Alb",
        "Oceanus Hesperos (Midgard)": "Oceanus Mid",
        "Oceanus Anatole (Hibernia)": "Oceanus Hib",
        "Oceanus Anatole (Albion)": "Oceanus Alb",
        "Oceanus Anatole (Midgard)": "Oceanus Mid",
        "Oceanus Boreas (Hibernia)": "Oceanus Hib",
        "Oceanus Boreas (Albion)": "Oceanus Alb",
        "Oceanus Boreas (Midgard)": "Oceanus Mid",
        "Deep Volcanus": "Volcanus",
        "Dragon's Lair": "DL",
        "Tuscan Glacier": "Epic",
        "Tuscaran Glacier": "Epic",
        "Galladoria": "Epic",
        "Caer Sidi": "Epic"
    }
    
    # Mapping zone → currency
    ZONE_CURRENCY = {
        "DF": "Seals",
        "SH": "Grimoires",
        "ToA": "Glasses",
        "Drake": "Scales",
        "Epic": "Souls/Roots/Ices",
        "Epik": "Souls/Roots/Ices"  # Ancienne orthographe
    }
    
    def __init__(self, eden_scraper):
        """
        Initialise le ItemsScraper avec un EdenScraper déjà connecté
        
        Args:
            eden_scraper: Instance de EdenScraper avec driver initialisé et cookies chargés
        """
        self.eden_scraper = eden_scraper
        self.driver = eden_scraper.driver
        self.logger = get_logger(LOGGER_EDEN)
        self.base_url = "https://eden-daoc.net/items"
        
        # Database path (embedded)
        self.database_file = Path(__file__).parent.parent / 'Data' / 'items_database_src.json'
        
        # Cache path (user profile)
        import os
        user_profile = os.getenv('LOCALAPPDATA') or os.getenv('APPDATA')
        if user_profile:
            cache_dir = Path(user_profile) / 'DAOC_Character_Manager' / 'ItemCache'
        else:
            # Fallback to Armory if env vars not available
            cache_dir = Path(__file__).parent.parent / 'Armory'
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / 'items_cache.json'
        
        # Initialize cache (web items only)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """
        Charge le cache des IDs d'items
        Le cache ne contient QUE les items trouvés via recherche web (pas ceux des databases)
        
        Returns:
            dict: Cache des items
        """
        try:
            # Check if user cache exists
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    self.logger.debug(f"Cache web chargé: {len(cache.get('items', {}))} items", 
                                    extra={"action": "CACHE"})
                    return cache
            else:
                # First run: create empty cache (no longer copies from database)
                self.logger.info("Premier démarrage: création d'un cache vide", 
                               extra={"action": "CACHE"})
                return self._create_empty_cache()
                
        except Exception as e:
            self.logger.warning(f"Erreur chargement cache: {e}", extra={"action": "CACHE"})
            return self._create_empty_cache()
    
    def _create_empty_cache(self):
        """
        Crée un cache vide pour les items trouvés via web uniquement
        
        Returns:
            dict: Cache vide initialisé
        """
        cache = {
            "version": "1.0",
            "description": "Web search cache - items NOT in databases",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": {}
        }
        
        # Create Armory folder if needed
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save empty cache
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=4, ensure_ascii=False)
            self.logger.info(f"✅ Cache web vide créé: {self.cache_file}", 
                           extra={"action": "CACHE"})
        except Exception as e:
            self.logger.warning(f"Erreur création cache: {e}", extra={"action": "CACHE"})
        
        return cache
    
    def _get_item_from_databases(self, item_name, realm=None):
        """
        Recherche un item dans les bases de données (source + user) avec clé composite
        Supporte fallback sur realm "all" si realm spécifique non trouvé
        
        Args:
            item_name: Nom de l'item
            realm: Royaume (optionnel)
            
        Returns:
            str: ID de l'item ou None si non trouvé
        """
        # Try realm-specific key first
        cache_key = self._get_cache_key(item_name, realm)
        
        # Check source database first (embedded)
        try:
            if self.database_file.exists():
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                    
                    # Direct lookup with realm
                    item_data = database.get("items", {}).get(cache_key)
                    if item_data and item_data.get('id'):
                        item_id = item_data.get('id')
                        self.logger.info(f"✅ Item trouvé dans DB source: {item_name} ({realm}) → ID {item_id}", 
                                       extra={"action": "DATABASE"})
                        return item_id
                    
                    # Fallback: try "all" realm if specific realm not found
                    if realm and realm != "All":
                        all_key = self._get_cache_key(item_name, "All")
                        item_data = database.get("items", {}).get(all_key)
                        if item_data and item_data.get('id'):
                            item_id = item_data.get('id')
                            self.logger.info(f"✅ Item trouvé dans DB source (All): {item_name} → ID {item_id}", 
                                           extra={"action": "DATABASE"})
                            return item_id
        except Exception as e:
            self.logger.debug(f"Erreur lecture DB source: {e}", extra={"action": "DATABASE"})
        
        # Check user database (Armory/items_database.json) if exists
        user_db_file = self.cache_file.parent / 'items_database.json'
        try:
            if user_db_file.exists():
                with open(user_db_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                    
                    # Direct lookup with realm
                    item_data = database.get("items", {}).get(cache_key)
                    if item_data and item_data.get('id'):
                        item_id = item_data.get('id')
                        self.logger.info(f"✅ Item trouvé dans DB user: {item_name} ({realm}) → ID {item_id}", 
                                       extra={"action": "DATABASE"})
                        return item_id
                    
                    # Fallback: try "all" realm
                    if realm and realm != "All":
                        all_key = self._get_cache_key(item_name, "All")
                        item_data = database.get("items", {}).get(all_key)
                        if item_data and item_data.get('id'):
                            item_id = item_data.get('id')
                            self.logger.info(f"✅ Item trouvé dans DB user (All): {item_name} → ID {item_id}", 
                                           extra={"action": "DATABASE"})
                            return item_id
        except Exception as e:
            self.logger.debug(f"Erreur lecture DB user: {e}", extra={"action": "DATABASE"})
        
        return None
    
    def _save_cache(self):
        """
        Sauvegarde le cache dans le fichier JSON
        """
        try:
            self.cache["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=4, ensure_ascii=False)
            
            self.logger.debug(f"Cache sauvegardé: {len(self.cache.get('items', {}))} items", 
                            extra={"action": "CACHE"})
        except Exception as e:
            self.logger.error(f"Erreur sauvegarde cache: {e}", extra={"action": "CACHE"})
    
    def _get_cache_key(self, item_name, realm=None):
        """
        Génère une clé de cache composite pour un item (DB v2.0)
        
        Args:
            item_name: Nom de l'item
            realm: Royaume (All/Albion/Hibernia/Midgard) - optionnel
        
        Returns:
            str: Clé composite "name:realm" (lowercase)
        """
        # Vérifier que item_name n'est pas None/vide
        if not item_name or not item_name.strip():
            raise ValueError("item_name cannot be None or empty")
        
        # Normaliser le nom (lowercase, strip)
        normalized_name = item_name.strip().lower()
        
        # Normaliser le royaume (défaut: "all")
        normalized_realm = (realm or "All").strip().lower()
        
        # Clé composite: "name:realm"
        return f"{normalized_name}:{normalized_realm}"
    
    def get_item_id_from_cache(self, item_name, realm=None):
        """
        Récupère l'ID d'un item depuis le cache
        
        Args:
            item_name: Nom de l'item
            realm: Royaume (optionnel, non utilisé car les noms sont uniques)
        
        Returns:
            str: ID de l'item ou None si non trouvé
        """
        cache_key = self._get_cache_key(item_name)
        item_data = self.cache.get("items", {}).get(cache_key)
        
        if item_data:
            item_id = item_data.get('id')
            item_display_name = item_data.get('name', item_name)
            self.logger.info(f"✅ Item trouvé dans cache: {item_display_name} (ID: {item_id})", 
                           extra={"action": "CACHE"})
            return item_id
        
        return None
    
    def save_item_to_cache(self, item_name, realm, item_id, item_data=None):
        """
        Sauvegarde un item dans le cache utilisateur
        
        Args:
            item_name: Nom de l'item
            realm: Royaume
            item_id: ID de l'item
            item_data: Données complètes de l'item (optionnel)
        """
        cache_key = self._get_cache_key(item_name)
        
        cache_entry = {
            "id": item_id,
            "name": item_name,
            "realm": realm,
            "cached_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Ajouter les données de l'item si disponibles
        if item_data:
            # Ajouter slot si disponible
            if item_data.get('slot'):
                cache_entry["slot"] = item_data.get('slot')
            
            # Ajouter info merchant si disponible
            merchants = item_data.get('merchants', [])
            if merchants:
                merchant = merchants[0]  # Premier vendeur
                cache_entry["merchant_zone"] = merchant.get('zone')
                
                # Prix : seulement le montant numérique
                price_parsed = merchant.get('price_parsed')
                if price_parsed:
                    cache_entry["merchant_price"] = str(price_parsed.get('amount'))
        
        self.cache["items"][cache_key] = cache_entry
        self._save_cache()
        
        self.logger.info(f"💾 Item sauvegardé dans cache: {item_name} (ID: {item_id})", 
                       extra={"action": "CACHE"})
    
    @staticmethod
    def parse_price(price_str):
        """
        Parse le prix et retourne un dict avec la monnaie et la quantité
        
        Args:
            price_str: String du prix (ex: "700 Grimoire Pages", "5p 50g", "100000 bounty points")
        
        Returns:
            dict: {'currency': str, 'amount': int/float, 'display': str}
        """
        if not price_str:
            return None
        
        price_str = price_str.strip().lower()
        
        # Atlantean Glass
        if 'atlantean glass' in price_str or 'glass' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Atlantean Glass', 'amount': amount, 'display': f"{amount} Atlantean Glass"}
            except:
                pass
        
        # Dragon Scales
        if 'dragon scale' in price_str or 'scales' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Dragon Scales', 'amount': amount, 'display': f"{amount} Dragon Scales"}
            except:
                pass
        
        # Aurulite
        if 'aurulite' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Aurulite', 'amount': amount, 'display': f"{amount} Aurulite"}
            except:
                pass
        
        # Orbs
        if 'orb' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Orbs', 'amount': amount, 'display': f"{amount} Orbs"}
            except:
                pass
        
        # Seals
        if 'seal' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Seals', 'amount': amount, 'display': f"{amount} Seals"}
            except:
                pass
        
        # Grimoire Pages
        if 'grimoire' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Grimoire Pages', 'amount': amount, 'display': f"{amount} Grimoire Pages"}
            except:
                pass
        
        # Bounty Points
        if 'bounty' in price_str or 'bp' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Bounty Points', 'amount': amount, 'display': f"{amount} BP"}
            except:
                pass
        
        # Roots (Galladoria)
        if 'root' in price_str:
            try:
                amount = int(price_str.split()[0])
                return {'currency': 'Roots', 'amount': amount, 'display': f"{amount} Roots"}
            except:
                pass
        
        # Gold/Platinum (format: "5p 50g 25s 10c" or "500g")
        if 'p' in price_str or 'g' in price_str or 's' in price_str or 'c' in price_str or 'plat' in price_str or 'gold' in price_str:
            total_copper = 0
            
            # Parse platinum
            if 'p' in price_str:
                match = re.search(r'(\d+)\s*p', price_str)
                if match:
                    total_copper += int(match.group(1)) * 100000000
            
            # Parse gold
            if 'g' in price_str:
                match = re.search(r'(\d+)\s*g', price_str)
                if match:
                    total_copper += int(match.group(1)) * 100000
            
            # Parse silver
            if 's' in price_str:
                match = re.search(r'(\d+)\s*s', price_str)
                if match:
                    total_copper += int(match.group(1)) * 100
            
            # Parse copper
            if 'c' in price_str:
                match = re.search(r'(\d+)\s*c', price_str)
                if match:
                    total_copper += int(match.group(1))
            
            if total_copper > 0:
                # Convert back to readable format
                plat = total_copper // 100000000
                gold = (total_copper % 100000000) // 100000
                silver = (total_copper % 100000) // 100
                copper = total_copper % 100
                
                display_parts = []
                if plat > 0:
                    display_parts.append(f"{plat}p")
                if gold > 0:
                    display_parts.append(f"{gold}g")
                if silver > 0:
                    display_parts.append(f"{silver}s")
                if copper > 0:
                    display_parts.append(f"{copper}c")
                
                return {
                    'currency': 'Gold',
                    'amount': total_copper,
                    'display': ', '.join(display_parts) if display_parts else '0c'
                }
        
        return None
        
    def navigate_to_market(self):
        """
        Navigue vers la page de la database items
        
        Returns:
            bool: True si la navigation a réussi
        """
        try:
            self.logger.info(f"Navigation vers {self.base_url}", extra={"action": "ITEMDB"})
            self.driver.get(self.base_url)
            
            # Wait longer for page load (items database may be slower)
            time.sleep(5)  # Increased from 2 to 5 seconds
            
            # Get current page source ONCE
            html_content = self.driver.page_source
            
            # Save HTML for debugging
            from pathlib import Path
            debug_file = Path(__file__).parent.parent / 'Logs' / 'debug_items_navigation.html'
            debug_file.parent.mkdir(exist_ok=True)
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"💾 HTML sauvegardé: {debug_file}", extra={"action": "ITEMDB"})
            
            # Check if page loaded correctly (use the SAME html_content)
            # Look for the specific error message, not just "not available" which can appear in help text
            if 'The requested page "items" is not available' in html_content:
                self.logger.error("❌ Page items database non disponible", extra={"action": "ITEMDB"})
                self.logger.error(f"   HTML taille: {len(html_content)} caractères", extra={"action": "ITEMDB"})
                return False
            
            self.logger.info("✅ Page items database chargée", extra={"action": "ITEMDB"})
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur navigation market: {e}", extra={"action": "ITEMDB"})
            return False
    
    def search_items(self, item_name=None, realm=None, class_filter=None, slot=None):
        """
        Recherche des items avec des filtres
        
        Args:
            item_name: Nom de l'item à rechercher (optionnel)
            realm: Royaume (All/Albion/Hibernia/Midgard)
            class_filter: Classe spécifique
            slot: Emplacement (Helmet, Hands, etc.)
            
        Returns:
            list: Liste de dictionnaires contenant les informations des items
                  [{
                      'name': str,
                      'realm': str,
                      'class': str,
                      'slot': str,
                      'level': int,
                      'quality': int,
                      'stats': dict
                  }]
        """
        try:
            # Navigate to market if not already there
            if self.base_url not in self.driver.current_url:
                if not self.navigate_to_market():
                    return []
            
            self.logger.info(f"🔍 Recherche items: name={item_name}, realm={realm}, class={class_filter}, slot={slot}", 
                           extra={"action": "ITEMDB"})
            
            # Apply filters if provided
            if realm:
                self._select_filter("select_realm", realm)
            
            if class_filter:
                self._select_filter("select_class", class_filter)
            
            if slot:
                self._select_filter("select_slot", slot)
            
            # Enter item name if provided
            if item_name:
                self._enter_search_text(item_name)
            
            # Click search button (if exists)
            # Note: Some filters auto-submit, need to check the page behavior
            time.sleep(1)
            
            # Parse results
            items = self._parse_search_results()
            
            self.logger.info(f"✅ {len(items)} items trouvés", extra={"action": "ITEMDB"})
            return items
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche items: {e}", extra={"action": "ITEMDB"})
            import traceback
            self.logger.debug(traceback.format_exc(), extra={"action": "ITEMDB"})
            return []
    
    def _select_filter(self, select_id, value):
        """
        Sélectionne une valeur dans un filtre dropdown
        
        Args:
            select_id: ID du select element
            value: Valeur à sélectionner (texte visible)
        """
        try:
            select_element = Select(self.driver.find_element(By.ID, select_id))
            select_element.select_by_visible_text(value)
            self.logger.debug(f"Filtre {select_id} = {value}", extra={"action": "ITEMDB"})
            time.sleep(0.5)  # Wait for potential AJAX reload
        except Exception as e:
            self.logger.warning(f"⚠️ Impossible de sélectionner {select_id}={value}: {e}", 
                              extra={"action": "ITEMDB"})
    
    def _enter_search_text(self, text):
        """
        Entre du texte dans le champ de recherche
        
        Args:
            text: Texte à rechercher
        """
        try:
            # Try common search input IDs/names
            search_inputs = [
                "search_name",
                "item_name",
                "name",
                "search"
            ]
            
            for input_id in search_inputs:
                try:
                    search_box = self.driver.find_element(By.ID, input_id)
                    search_box.clear()
                    search_box.send_keys(text)
                    self.logger.debug(f"Texte recherche '{text}' entré dans {input_id}", 
                                    extra={"action": "ITEMDB"})
                    return
                except:
                    continue
            
            self.logger.warning(f"⚠️ Champ de recherche non trouvé", extra={"action": "ITEMDB"})
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur saisie recherche: {e}", extra={"action": "ITEMDB"})
    
    def _parse_search_results(self):
        """
        Parse les résultats de recherche sur la page
        
        Returns:
            list: Liste d'items avec leurs informations
        """
        try:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = []
            
            # Look for result tables or item containers
            # The structure will depend on how Eden displays results
            # Common patterns: tables, divs with class "item", "result", etc.
            
            # Strategy 1: Look for tables
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                # Skip header row
                for row in rows[1:]:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 4:  # Minimum expected columns
                        item_data = self._extract_item_from_row(cells)
                        if item_data:
                            items.append(item_data)
            
            # Strategy 2: Look for item divs/containers
            item_containers = soup.find_all(['div', 'li'], class_=lambda x: x and 'item' in x.lower())
            
            for container in item_containers:
                item_data = self._extract_item_from_container(container)
                if item_data:
                    items.append(item_data)
            
            return items
            
        except Exception as e:
            self.logger.error(f"❌ Erreur parsing résultats: {e}", extra={"action": "ITEMDB"})
            return []
    
    def _extract_item_from_row(self, cells):
        """
        Extrait les informations d'un item depuis une ligne de tableau
        
        Args:
            cells: Liste de cellules (td) de la ligne
            
        Returns:
            dict: Informations de l'item ou None
        """
        try:
            # This is a template - structure depends on actual HTML
            # Need to inspect actual search results to determine column order
            
            item = {
                'name': None,
                'realm': None,
                'class': None,
                'slot': None,
                'level': None,
                'quality': None,
                'stats': {}
            }
            
            # Try to extract common fields
            # Column order needs to be determined from actual results
            for i, cell in enumerate(cells):
                text = cell.get_text(strip=True)
                
                # Try to identify field by content/class/attribute
                if i == 0:  # Typically item name
                    item['name'] = text
                elif 'realm' in str(cell).lower():
                    item['realm'] = text
                elif 'class' in str(cell).lower():
                    item['class'] = text
                elif 'slot' in str(cell).lower():
                    item['slot'] = text
            
            # Only return if we got at least a name
            if item['name']:
                return item
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Erreur extraction row: {e}", extra={"action": "ITEMDB"})
            return None
    
    def _extract_item_from_container(self, container):
        """
        Extrait les informations d'un item depuis un container div/li
        
        Args:
            container: Element BeautifulSoup contenant l'item
            
        Returns:
            dict: Informations de l'item ou None
        """
        try:
            item = {
                'name': None,
                'realm': None,
                'class': None,
                'slot': None,
                'level': None,
                'quality': None,
                'stats': {}
            }
            
            # Look for common patterns
            name_elem = container.find(['h3', 'h4', 'span', 'a'], class_=lambda x: x and 'name' in x.lower())
            if name_elem:
                item['name'] = name_elem.get_text(strip=True)
            
            # Extract other fields based on actual HTML structure
            # This is a template that will need adjustment
            
            if item['name']:
                return item
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Erreur extraction container: {e}", extra={"action": "ITEMDB"})
            return None
    
    def get_all_items_by_slot(self, slot, realm=None):
        """
        Récupère tous les items d'un slot spécifique
        
        Args:
            slot: Emplacement (Helmet, Hands, Torso, etc.)
            realm: Royaume optionnel pour filtrer
            
        Returns:
            list: Liste d'items pour ce slot
        """
        return self.search_items(slot=slot, realm=realm)
    
    def find_item_id(self, item_name, realm="All", force_scrape=False, skip_filters=False):
        """
        Recherche l'ID d'un item pour un realm spécifique.
        
        ATTENTION: Cette fonction recherche UNE SEULE variante.
        Pour alimenter la DB avec toutes les variantes, utiliser find_all_item_variants()
        
        Recherche dans cet ordre:
        1. Bases de données (source + user) - sauf si force_scrape=True
        2. Cache web
        3. Recherche en ligne sur Eden (r=0 puis filtrage par realm)
        
        Args:
            item_name: Nom de l'item
            realm: Royaume spécifique (Hibernia, Albion, Midgard, All)
            force_scrape: Si True, ignore les DBs et force la recherche web
            skip_filters: Si True, ignore les filtres level/utility (retry mode)
        
        Returns:
            str: ID de l'item pour ce realm ou None
        """
        # 1. Check databases first (embedded + user) - skip if force_scrape
        if not force_scrape:
            db_id = self._get_item_from_databases(item_name, realm)
            if db_id:
                return db_id
        
        # 2. Check web cache (items found via previous web searches)
        cached_id = self.get_item_id_from_cache(item_name, realm)
        if cached_id:
            self.logger.info(f"🎯 ID trouvé dans le cache web: {cached_id}", extra={"action": "CACHE"})
            return cached_id
        
        # 3. Search online - utilise la nouvelle logique r=0 + filtrage
        self.logger.info(f"⚠️ Item non trouvé (DB/cache), recherche en ligne...", extra={"action": "SEARCH"})
        
        # Utiliser find_all_item_variants puis filtrer par realm (with optional skip_filters)
        variants = self.find_all_item_variants(item_name, skip_filters=skip_filters)
        
        if not variants:
            return None
        
        # Filtrer par realm demandé
        for variant in variants:
            if variant['realm'] == realm or variant['realm'] == 'All' or realm == 'All':
                item_id = variant['id']
                self.logger.info(f"✅ ID trouvé pour {realm}: {item_id}", extra={"action": "ITEMDB"})
                self.save_item_to_cache(item_name, realm, item_id)
                return item_id
        
        # Si aucun match exact, prendre le premier
        if variants:
            item_id = variants[0]['id']
            self.logger.warning(f"⚠️ Aucun match exact pour realm '{realm}', utilise premier résultat: {item_id}", extra={"action": "ITEMDB"})
            self.save_item_to_cache(item_name, realm, item_id)
            return item_id
        
        return None
    
    def find_all_item_variants(self, item_name, return_filtered=False, skip_filters=False):
        """
        Trouve TOUTES les variantes d'un item (tous les realms).
        Utilisé pour alimenter la DB avec toutes les versions disponibles.
        
        Args:
            item_name: Nom de l'item à rechercher
            return_filtered: Si True, retourne aussi les items filtrés avec raisons
            skip_filters: Si True, ignore les filtres level/utility (retry mode)
        
        Returns:
            Si return_filtered=False:
                List[Dict]: Liste de toutes les variantes trouvées
            Si return_filtered=True:
                Tuple[List[Dict], List[Dict]]: (variants, filtered_items)
                filtered_items contient: [{'name': ..., 'realm': ..., 'reason': ..., 'level': ..., 'utility': ...}]
        """
        try:
            # Build search URL avec r=0 (ALL realms)
            import urllib.parse
            search_encoded = urllib.parse.quote(item_name)
            search_url = f"{self.base_url}?s={search_encoded}&r=0"
            
            if skip_filters:
                self.logger.info(f"🔍 Recherche TOUTES variantes (SANS FILTRES): {item_name}", extra={"action": "ITEMDB"})
            else:
                self.logger.info(f"🔍 Recherche TOUTES variantes: {item_name}", extra={"action": "ITEMDB"})
            self.logger.debug(f"📍 URL: {search_url}", extra={"action": "ITEMDB"})
            
            # Navigate to search URL
            self.driver.get(search_url)
            
            # Wait for results table to load
            self.logger.debug("⏳ Attente chargement des résultats...", extra={"action": "ITEMDB"})
            time.sleep(8)
            
            # Wait for table results
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "table_result"))
                )
                self.logger.debug("✅ Table de résultats chargée", extra={"action": "ITEMDB"})
            except:
                self.logger.warning("⚠️ Timeout attente table résultats", extra={"action": "ITEMDB"})
            
            # Small additional wait for JavaScript population
            time.sleep(3)
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Collecter TOUS les result_row avec leur icône realm
            variants = []
            filtered_items = []  # Initialize filtered items list
            result_rows = soup.find_all('tr', id=re.compile(r'^result_row_\d+$'))
            
            # Counters for filtering reasons
            skip_reasons = {
                'name_mismatch': 0,
                'level_too_low': 0,
                'utility_too_low': 0,
                'no_realm_icon': 0,
                'no_name_cell': 0,
                'no_merchant': 0,
                'currency_not_supported': 0
            }
            
            self.logger.info(f"📊 {len(result_rows)} résultat(s) brut(s) trouvé(s)", extra={"action": "ITEMDB"})
            
            # 🔍 DEBUG: Afficher la structure de la première ligne pour analyse
            if result_rows and len(result_rows) > 0:
                first_row = result_rows[0]
                cells = first_row.find_all('td')
                self.logger.debug(f"🔍 DEBUG - Structure de la première ligne ({len(cells)} colonnes):", extra={"action": "ITEMDB"})
                for idx, cell in enumerate(cells):
                    content = cell.get_text(strip=True)[:50]  # Limite à 50 caractères
                    img = cell.find('img')
                    img_src = img.get('src', '') if img else 'NO IMAGE'
                    self.logger.debug(f"  Colonne {idx}: '{content}' | Image: {img_src}", extra={"action": "ITEMDB"})
            
            for row in result_rows:
                # Extraire l'ID depuis result_row_XXXXX
                row_id = row.get('id', '')
                match = re.search(r'result_row_(\d+)', row_id)
                if not match:
                    continue
                
                item_id = match.group(1)
                
                # DEBUG: Afficher toutes les cellules de cette ligne
                all_cells = row.find_all('td')
                self.logger.debug(f"🔍 Processing ID {item_id} - {len(all_cells)} colonnes", extra={"action": "ITEMDB"})
                
                # Extraire les valeurs de toutes les colonnes de façon robuste
                cells_text = [cell.get_text(strip=True) for cell in all_cells]
                
                # FILTRAGE 1: Vérifier le NOM EXACT (case-insensitive)
                # La colonne avec le nom est généralement la 2ème <td> (index 1)
                # Mais on cherche aussi dans les autres colonnes si ce n'est pas là
                name_cell = all_cells[1] if len(all_cells) > 1 else None
                if name_cell:
                    found_name = name_cell.get_text(strip=True)
                    # Comparaison case-insensitive
                    if found_name.lower() != item_name.lower():
                        skip_reasons['name_mismatch'] += 1
                        self.logger.debug(f"  ⏭️  SKIP (nom différent): '{found_name}' != '{item_name}'", extra={"action": "ITEMDB"})
                        # Don't store name mismatch in filtered_items (not the item we're looking for)
                        continue
                else:
                    skip_reasons['no_name_cell'] += 1
                    self.logger.warning(f"  ⚠️ Impossible de trouver le nom pour ID {item_id}", extra={"action": "ITEMDB"})
                    continue
                
                # FILTRAGE 2: Vérifier le LEVEL ≥ 50
                # Chercher dynamiquement la colonne qui contient un nombre entre 1 et 51
                level = None
                level_idx = None
                level_text = "N/A"
                for idx, text in enumerate(cells_text):
                    if idx == 0 or idx == 1:  # Skip icône et nom
                        continue
                    try:
                        val = int(text)
                        if 1 <= val <= 51:  # Level DAOC range
                            level = val
                            level_idx = idx
                            level_text = text
                            self.logger.debug(f"  ✓ Level trouvé: {level} (colonne {idx})", extra={"action": "ITEMDB"})
                            break
                    except ValueError:
                        continue
                
                if level is not None and level < 50:
                    if not skip_filters:
                        skip_reasons['level_too_low'] += 1
                        self.logger.debug(f"  ⏭️  SKIP (level < 50): Level {level} pour '{found_name}'", extra={"action": "ITEMDB"})
                        # Store in filtered_items (we need realm first)
                        # Will be completed after realm extraction
                        filtered_info = {
                            'name': found_name,
                            'id': item_id,
                            'reason': 'level_too_low',
                            'level': level,
                            'utility': None  # Will be filled if found
                        }
                        # Continue to get realm before storing
                        skip_level = True
                    else:
                        self.logger.debug(f"  ✓ Level {level} (filter bypassed)", extra={"action": "ITEMDB"})
                        skip_level = False
                else:
                    skip_level = False
                
                # FILTRAGE 3: Vérifier UTILITY ≥ 100
                # Chercher dynamiquement la colonne qui contient un nombre décimal > 50
                # IMPORTANT: Sauter la colonne du level trouvé précédemment
                utility = None
                utility_text = "N/A"
                for idx, text in enumerate(cells_text):
                    if idx == 0 or idx == 1:  # Skip icône et nom
                        continue
                    if level_idx is not None and idx == level_idx:  # SKIP la colonne level
                        continue
                    try:
                        val = float(text)
                        if val >= 50:  # Utility généralement > 50
                            utility = val
                            utility_text = text
                            self.logger.debug(f"  ✓ Utility trouvée: {utility} (colonne {idx})", extra={"action": "ITEMDB"})
                            break
                    except ValueError:
                        continue
                
                if utility is not None and utility < 100:
                    if not skip_filters:
                        skip_reasons['utility_too_low'] += 1
                        self.logger.debug(f"  ⏭️  SKIP (utility < 100): Utility {utility} pour '{found_name}'", extra={"action": "ITEMDB"})
                        filtered_info = {
                            'name': found_name,
                            'id': item_id,
                            'reason': 'utility_too_low',
                            'level': level,
                            'utility': utility
                        }
                        skip_utility = True
                    else:
                        self.logger.debug(f"  ✓ Utility {utility} (filter bypassed)", extra={"action": "ITEMDB"})
                        skip_utility = False
                elif utility is None:
                    self.logger.debug(f"  ℹ️ Pas de colonne utility trouvée pour '{found_name}' (ID {item_id}), on continue", extra={"action": "ITEMDB"})
                    skip_utility = False
                    if 'filtered_info' in locals() and 'skip_level' in locals() and skip_level:
                        filtered_info['utility'] = None
                else:
                    skip_utility = False
                    if 'filtered_info' in locals() and 'skip_level' in locals() and skip_level:
                        filtered_info['utility'] = utility
                
                # Extraire le realm depuis l'icône (OBLIGATOIRE)
                # Chercher l'icône avec différents chemins possibles
                realm_img = row.find('img', src=re.compile(r'(albion_logo|hibernia_logo|midgard_logo|all_logo)\.png'))
                if not realm_img:
                    skip_reasons['no_realm_icon'] += 1
                    self.logger.warning(f"⚠️ Pas d'icône realm pour '{found_name}' (ID {item_id}), SKIP", extra={"action": "ITEMDB"})
                    continue
                
                src = realm_img.get('src', '')
                if 'albion_logo' in src:
                    item_realm = 'Albion'
                elif 'hibernia_logo' in src:
                    item_realm = 'Hibernia'
                elif 'midgard_logo' in src:
                    item_realm = 'Midgard'
                elif 'all_logo' in src:
                    item_realm = 'All'
                else:
                    self.logger.warning(f"⚠️ Icône realm inconnue: {src}, SKIP", extra={"action": "ITEMDB"})
                    continue
                
                # If item was filtered, store it with realm info before skipping
                if 'skip_level' in locals() and skip_level:
                    filtered_info['realm'] = item_realm
                    filtered_items.append(filtered_info)
                    del filtered_info, skip_level  # Clean up
                    continue
                
                if 'skip_utility' in locals() and skip_utility:
                    filtered_info['realm'] = item_realm
                    filtered_items.append(filtered_info)
                    del filtered_info, skip_utility  # Clean up
                    continue
                
                variant = {
                    'id': item_id,
                    'realm': item_realm,
                    'name': found_name  # Utiliser le nom trouvé (casse originale)
                }
                variants.append(variant)
                self.logger.debug(f"  ✓ Variante VALIDE: {item_realm} → ID {item_id} (Level {level_text if level_text else 'N/A'})", extra={"action": "ITEMDB"})
            
            if not variants:
                # Build detailed error message
                total_skipped = sum(skip_reasons.values())
                reasons_str = []
                
                if skip_reasons['name_mismatch'] > 0:
                    reasons_str.append(f"{skip_reasons['name_mismatch']} nom différent")
                if skip_reasons['level_too_low'] > 0:
                    reasons_str.append(f"{skip_reasons['level_too_low']} level < 50")
                if skip_reasons['utility_too_low'] > 0:
                    reasons_str.append(f"{skip_reasons['utility_too_low']} utility < 100")
                if skip_reasons['no_realm_icon'] > 0:
                    reasons_str.append(f"{skip_reasons['no_realm_icon']} pas d'icône realm")
                if skip_reasons['no_name_cell'] > 0:
                    reasons_str.append(f"{skip_reasons['no_name_cell']} nom introuvable")
                if skip_reasons['no_merchant'] > 0:
                    reasons_str.append(f"{skip_reasons['no_merchant']} pas de vendeur")
                if skip_reasons['currency_not_supported'] > 0:
                    reasons_str.append(f"{skip_reasons['currency_not_supported']} devise non-supportée (BP/Bounty/etc.)")
                
                if total_skipped > 0 and reasons_str:
                    reason_detail = ", ".join(reasons_str)
                    self.logger.warning(
                        f"❌ Aucune variante trouvée pour '{item_name}' - {len(result_rows)} résultat(s) ignoré(s): {reason_detail}",
                        extra={"action": "ITEMDB"}
                    )
                elif len(result_rows) == 0:
                    self.logger.warning(f"❌ Aucun résultat trouvé pour '{item_name}' sur Eden", extra={"action": "ITEMDB"})
                else:
                    self.logger.warning(f"❌ Aucune variante trouvée pour '{item_name}' (raison inconnue)", extra={"action": "ITEMDB"})
            else:
                total_skipped = sum(skip_reasons.values())
                if total_skipped > 0:
                    self.logger.info(
                        f"✅ {len(variants)} variante(s) trouvée(s) pour '{item_name}' ({total_skipped} résultat(s) filtré(s))",
                        extra={"action": "ITEMDB"}
                    )
                else:
                    self.logger.info(f"✅ {len(variants)} variante(s) trouvée(s) pour '{item_name}'", extra={"action": "ITEMDB"})
            
            if return_filtered:
                self.logger.debug(f"🔍 Returning {len(variants)} variants and {len(filtered_items)} filtered items", extra={"action": "ITEMDB"})
                return variants, filtered_items
            else:
                return variants
            
        except Exception as e:
            self.logger.error(f"Erreur recherche variantes: {e}", extra={"action": "ITEMDB"})
            import traceback
            self.logger.debug(traceback.format_exc(), extra={"action": "ITEMDB"})
            if return_filtered:
                return [], []
            else:
                return []
    
    def get_item_details(self, item_id, realm="All", item_name=None):
        """
        Récupère les détails complets d'un item via son ID
        
        Args:
            item_id: ID de l'item
            realm: Royaume (pour contexte)
            item_name: Nom de l'item (pour recherche si besoin)
        
        Returns:
            dict: Détails complets de l'item avec merchants, stats, etc.
        """
        try:
            self.logger.info(f"📄 Récupération détails item ID: {item_id}", extra={"action": "ITEMDB"})
            
            # Try to find and click on the item row in search results
            try:
                row = self.driver.find_element(By.ID, f"result_row_{item_id}")
                row.click()
                self.logger.debug("✅ Clic sur l'item effectué", extra={"action": "ITEMDB"})
                time.sleep(2)
                
            except Exception as e:
                # If row not found, navigate directly to item URL
                self.logger.debug(f"Row non trouvé, navigation directe vers l'item", extra={"action": "ITEMDB"})
                
                item_url = f"{self.base_url}?id={item_id}"
                self.driver.get(item_url)
                time.sleep(3)
                self.logger.debug(f"✅ Navigation directe vers {item_url}", extra={"action": "ITEMDB"})
            
            # Wait for item details to load via JavaScript
            self.logger.debug("⏳ Attente chargement détails item...", extra={"action": "ITEMDB"})
            
            # Wait for item details table with actual data (not empty search table)
            # We need to wait for table rows with class "item_line_left" which contain the actual item data
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "item_line_left"))
                )
                self.logger.debug("✅ Détails item chargés (lignes item_line_left trouvées)", extra={"action": "ITEMDB"})
            except Exception as e:
                self.logger.warning(f"⚠️ Timeout attente détails item: {e}", extra={"action": "ITEMDB"})
            
            # Additional wait for complete rendering
            time.sleep(2)
            
            # DEBUG: Save HTML for inspection
            from pathlib import Path
            debug_folder = Path(__file__).parent.parent / 'Logs' / 'items_details_debug'
            debug_folder.mkdir(parents=True, exist_ok=True)
            debug_file = debug_folder / f"item_{item_id}_clicked.html"
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            self.logger.debug(f"💾 HTML détails sauvegardé: {debug_file}", extra={"action": "ITEMDB"})
            
            # Parse page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            item_data = {
                'id': item_id,
                'name': None,
                'type': None,
                'slot': None,
                'realm': realm,
                'model': None,        # Model ID (visual appearance)
                'dps': None,          # Damage Per Second (weapons only)
                'speed': None,        # Weapon Speed (weapons only)
                'damage_type': None,  # Crush/Slash/Thrust (weapons only)
                'usable_by': 'ALL',   # Classes that can use this item (default: ALL)
                'merchants': []
            }
            
            # Extract data from HTML table (only reliable source)
            
            # Find the main result table
            result_table = soup.find('table', id='table_result')
            if not result_table:
                self.logger.error("❌ Table résultat introuvable", extra={"action": "ITEMDB"})
                return item_data
            
            # Extract item name from the first <tr> with class="header" containing the item name
            # The name is in a <td class="nowrap"> element (second column of header row)
            all_rows = result_table.find_all('tr')
            for row in all_rows:
                # Check if this row has the header class
                if row.find('td', class_='header'):
                    # Find the nowrap cell that contains the item name (not icon or stats)
                    nowrap_cells = row.find_all('td', class_='nowrap')
                    for cell in nowrap_cells:
                        # Skip cells with icons (those have width style)
                        if not cell.get('style') or 'width' not in cell.get('style', ''):
                            text = cell.get_text(strip=True)
                            # Check if it's not utility text (contains numbers like "103.0")
                            if text and not any(char.isdigit() for char in text):
                                item_data['name'] = text
                                self.logger.debug(f"📝 Nom extrait: {item_data['name']}", extra={"action": "ITEMDB"})
                                break
                if item_data['name']:
                    break
            
            # Find all item detail lines (class="item_line_left" and "item_line_right")
            detail_rows = result_table.find_all('tr')
            for row in detail_rows:
                cells = row.find_all('td')
                if len(cells) == 2:
                    left_cell = cells[0]
                    right_cell = cells[1]
                    
                    # Check if this is a detail row
                    if 'item_line_left' in left_cell.get('class', []):
                        label = left_cell.get_text(strip=True)
                        value = right_cell.get_text(strip=True)
                        
                        # Map the label to our data structure
                        if label == 'Type':
                            item_data['type'] = value
                            self.logger.debug(f"  Type: {value}", extra={"action": "ITEMDB"})
                        elif label == 'Slot':
                            item_data['slot'] = value
                            self.logger.debug(f"  Slot: {value}", extra={"action": "ITEMDB"})
                        elif label == 'Realm':
                            item_data['realm'] = value
                        # Model ID
                        elif label == 'Model':
                            item_data['model'] = value
                            self.logger.debug(f"  Model: {value}", extra={"action": "ITEMDB"})
                        # Damage Info (weapons only)
                        elif label == 'DPS':
                            item_data['dps'] = value
                            self.logger.debug(f"  DPS: {value}", extra={"action": "ITEMDB"})
                        elif label == 'Speed':
                            item_data['speed'] = value
                            self.logger.debug(f"  Speed: {value}", extra={"action": "ITEMDB"})
                        elif label == 'Damage Type':
                            item_data['damage_type'] = value
                            self.logger.debug(f"  Damage Type: {value}", extra={"action": "ITEMDB"})
                        # Usable by (classes)
                        elif label == 'Usable by':
                            item_data['usable_by'] = value if value else 'ALL'
                            self.logger.debug(f"  Usable by: {value}", extra={"action": "ITEMDB"})
            
            # Parse merchants section
            merchants_table = soup.find('table', id='table_merchants')
            if merchants_table:
                # Find all merchant divs
                merchant_divs = merchants_table.find_all('div', class_='item_mob')
                for merchant_div in merchant_divs:
                    merchant_data = {
                        'name': None,
                        'level': None,
                        'location': None,
                        'zone': None,
                        'zone_full': None,
                        'price': None,
                        'price_parsed': None
                    }
                    
                    # Find all rows in the merchant div
                    merchant_rows = merchant_div.find_all('tr')
                    for row in merchant_rows:
                        cells = row.find_all('td')
                        if not cells:
                            continue
                        
                        row_text = row.get_text(strip=True)
                        
                        # Name and level row (has "Level:" in it)
                        if 'Level:' in row_text:
                            # Name is in the clickable element
                            name_elem = row.find('td', class_='mob_name')
                            if name_elem:
                                merchant_data['name'] = name_elem.get_text(strip=True)
                            # Level is in the right cell
                            if len(cells) >= 2:
                                level_text = cells[-1].get_text(strip=True)
                                level_match = re.search(r'Level:\s*(\d+)', level_text)
                                if level_match:
                                    merchant_data['level'] = level_match.group(1)
                        
                        # Zone row (starts with "in ")
                        elif row_text.startswith('in '):
                            zone_full = row_text.replace('in ', '').split('Loc:')[0].strip()
                            zone_short = self.ZONE_MAPPING.get(zone_full, zone_full)
                            merchant_data['zone'] = zone_short
                            merchant_data['zone_full'] = zone_full
                            
                            # Location (Loc: xxx)
                            if 'Loc:' in row_text:
                                loc_match = re.search(r'Loc:\s*(.+?)$', row_text)
                                if loc_match:
                                    merchant_data['location'] = loc_match.group(1).strip()
                        
                        # Price row
                        elif row_text.startswith('Price:'):
                            price_text = row_text.replace('Price:', '').strip()
                            merchant_data['price'] = price_text
                            merchant_data['price_parsed'] = self.parse_price(price_text)
                            
                            # Override zone based on currency
                            if merchant_data['price_parsed']:
                                currency = merchant_data['price_parsed']['currency']
                                if currency == 'Atlantean Glass':
                                    merchant_data['zone'] = 'ToA'
                                elif currency == 'Seals':
                                    merchant_data['zone'] = 'DF'
                                elif currency in ['Roots', 'Souls', 'Ices']:
                                    merchant_data['zone'] = 'Epic'
                                elif currency == 'Dragon Scales':
                                    # Afficher "Scales" comme devise
                                    merchant_data['price_parsed']['currency'] = 'Scales'
                                    merchant_data['zone'] = 'Drake'
                                elif currency == 'Scales':
                                    merchant_data['zone'] = 'Drake'
                                elif currency == 'Grimoires':
                                    merchant_data['zone'] = 'SH'
                    
                    # Add merchant if we found a name
                    if merchant_data['name']:
                        item_data['merchants'].append(merchant_data)
            
            # Extraire merchant_zone, merchant_price et merchant_currency du premier vendeur pour la DB
            if item_data['merchants']:
                first_merchant = item_data['merchants'][0]
                zone = first_merchant.get('zone')
                item_data['merchant_zone'] = zone
                if first_merchant.get('price_parsed'):
                    item_data['merchant_price'] = str(first_merchant['price_parsed'].get('amount'))
                # Ajouter la currency basée sur la zone
                item_data['merchant_currency'] = self.ZONE_CURRENCY.get(zone)
            
            return item_data
            
        except Exception as e:
            self.logger.error(f"Erreur récupération détails item: {e}", extra={"action": "ITEMDB"})
            # Return minimal data with ID instead of None
            return {
                'id': item_id,
                'name': item_name if item_name else 'Unknown',
                'error': str(e)
            }
