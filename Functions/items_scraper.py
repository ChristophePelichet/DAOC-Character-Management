#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Items Scraper - Récupération des données de la Database Items Eden
Permet de rechercher et extraire les informations des items
"""

import time
import json
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
        "Tuscan Glacier": "Glacier",
        "Galladoria": "Galladoria"
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
        
        # Database and cache paths
        self.database_file = Path(__file__).parent.parent / 'Data' / 'items_database.json'
        self.cache_file = Path(__file__).parent.parent / 'Armory' / 'items_cache.json'
        
        # Initialize cache (will copy from database if needed)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """
        Charge le cache des IDs d'items
        Si le cache n'existe pas, le crée depuis la base de données embarquée
        
        Returns:
            dict: Cache des items
        """
        try:
            # Check if user cache exists
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    self.logger.debug(f"Cache utilisateur chargé: {len(cache.get('items', {}))} items", 
                                    extra={"action": "CACHE"})
                    return cache
            else:
                # First run: copy from database to cache
                self.logger.info("Premier démarrage: création du cache depuis la base de données", 
                               extra={"action": "CACHE"})
                return self._initialize_cache_from_database()
                
        except Exception as e:
            self.logger.warning(f"Erreur chargement cache: {e}", extra={"action": "CACHE"})
            # Fallback: try to load from database
            return self._initialize_cache_from_database()
    
    def _initialize_cache_from_database(self):
        """
        Initialise le cache utilisateur depuis la base de données embarquée
        
        Returns:
            dict: Cache initialisé
        """
        try:
            # Load embedded database
            if self.database_file.exists():
                with open(self.database_file, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                
                self.logger.info(f"Base de données chargée: {len(database.get('items', {}))} items", 
                               extra={"action": "CACHE"})
                
                # Create Armory folder if needed
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Create user cache from database
                cache = {
                    "version": database.get("version", "1.0"),
                    "description": "User items cache - customizable",
                    "source": "Copied from Data/items_database.json",
                    "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "items": database.get("items", {})
                }
                
                # Save initial cache
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, indent=4, ensure_ascii=False)
                
                self.logger.info(f"✅ Cache utilisateur créé: {self.cache_file}", 
                               extra={"action": "CACHE"})
                
                return cache
                
        except Exception as e:
            self.logger.error(f"Erreur initialisation cache depuis base: {e}", 
                            extra={"action": "CACHE"})
        
        # Return empty cache if all fails
        return {
            "version": "1.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "items": {}
        }
    
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
        Génère une clé de cache unique pour un item
        
        Args:
            item_name: Nom de l'item
            realm: Royaume (All/Albion/Hibernia/Midgard) - optionnel
        
        Returns:
            str: Clé de cache
        """
        # Normaliser le nom (lowercase, strip)
        normalized_name = item_name.strip().lower()
        
        # Pour la recherche, on ignore le royaume car les items ont des noms uniques
        # La clé est juste le nom normalisé
        return normalized_name
    
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
            self.logger.info(f"Navigation vers {self.base_url}", extra={"action": "MARKET"})
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
            self.logger.info(f"💾 HTML sauvegardé: {debug_file}", extra={"action": "MARKET"})
            
            # Check if page loaded correctly (use the SAME html_content)
            # Look for the specific error message, not just "not available" which can appear in help text
            if 'The requested page "items" is not available' in html_content:
                self.logger.error("❌ Page items database non disponible", extra={"action": "MARKET"})
                self.logger.error(f"   HTML taille: {len(html_content)} caractères", extra={"action": "MARKET"})
                return False
            
            self.logger.info("✅ Page items database chargée", extra={"action": "MARKET"})
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur navigation market: {e}", extra={"action": "MARKET"})
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
                           extra={"action": "MARKET"})
            
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
            
            self.logger.info(f"✅ {len(items)} items trouvés", extra={"action": "MARKET"})
            return items
            
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche items: {e}", extra={"action": "MARKET"})
            import traceback
            self.logger.debug(traceback.format_exc(), extra={"action": "MARKET"})
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
            self.logger.debug(f"Filtre {select_id} = {value}", extra={"action": "MARKET"})
            time.sleep(0.5)  # Wait for potential AJAX reload
        except Exception as e:
            self.logger.warning(f"⚠️ Impossible de sélectionner {select_id}={value}: {e}", 
                              extra={"action": "MARKET"})
    
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
                                    extra={"action": "MARKET"})
                    return
                except:
                    continue
            
            self.logger.warning(f"⚠️ Champ de recherche non trouvé", extra={"action": "MARKET"})
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erreur saisie recherche: {e}", extra={"action": "MARKET"})
    
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
            self.logger.error(f"❌ Erreur parsing résultats: {e}", extra={"action": "MARKET"})
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
            self.logger.debug(f"Erreur extraction row: {e}", extra={"action": "MARKET"})
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
            self.logger.debug(f"Erreur extraction container: {e}", extra={"action": "MARKET"})
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
    
    def find_item_id(self, item_name, realm="All"):
        """
        Recherche l'ID d'un item sur Eden (avec cache)
        
        Args:
            item_name: Nom de l'item
            realm: Royaume (Hibernia, Albion, Midgard, All)
        
        Returns:
            str: ID de l'item ou None
        """
        # Check cache first
        cached_id = self.get_item_id_from_cache(item_name, realm)
        if cached_id:
            self.logger.info(f"🎯 ID trouvé dans le cache: {cached_id}", extra={"action": "CACHE"})
            return cached_id
        
        self.logger.info(f"⚠️ Item non trouvé dans le cache, recherche en ligne...", extra={"action": "CACHE"})
        
        try:
            # Build search URL
            realm_id = self.REALM_MAP.get(realm, 0)
            import urllib.parse
            search_encoded = urllib.parse.quote(item_name)
            search_url = f"{self.base_url}?s={search_encoded}&r={realm_id}"
            
            self.logger.info(f"🔍 Recherche: {item_name} ({realm})", extra={"action": "MARKET"})
            self.logger.debug(f"📍 URL: {search_url}", extra={"action": "MARKET"})
            
            # Navigate to search URL
            self.driver.get(search_url)
            
            # Wait for results table to load
            self.logger.debug("⏳ Attente chargement des résultats...", extra={"action": "MARKET"})
            time.sleep(8)
            
            # Wait for table results
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "table_result"))
                )
                self.logger.debug("✅ Table de résultats chargée", extra={"action": "MARKET"})
            except:
                self.logger.warning("⚠️ Timeout attente table résultats", extra={"action": "MARKET"})
            
            # Small additional wait for JavaScript population
            time.sleep(3)
            
            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find all onclick links that contain "item_go"
            item_id = None
            for link in soup.find_all('a', onclick=True):
                onclick = link.get('onclick', '')
                if 'item_go' in onclick:
                    # Extract ID from onclick="item_go(ID)"
                    match = re.search(r'item_go\((\d+)\)', onclick)
                    if match:
                        item_id = match.group(1)
                        self.logger.info(f"✅ ID trouvé: {item_id}", extra={"action": "MARKET"})
                        
                        # Save to cache
                        self.save_item_to_cache(item_name, realm, item_id)
                        return item_id
            
            self.logger.warning(f"❌ ID non trouvé pour: {item_name}", extra={"action": "MARKET"})
            return None
            
        except Exception as e:
            self.logger.error(f"Erreur recherche item ID: {e}", extra={"action": "MARKET"})
            return None
    
    def get_item_details(self, item_id, realm="All"):
        """
        Récupère les détails complets d'un item via son ID
        
        Args:
            item_id: ID de l'item
            realm: Royaume (pour contexte)
        
        Returns:
            dict: Détails complets de l'item avec merchants, stats, etc.
        """
        try:
            # Navigate to item details page
            item_url = f"{self.base_url}?id={item_id}"
            self.logger.info(f"📄 Récupération détails item ID: {item_id}", extra={"action": "MARKET"})
            self.driver.get(item_url)
            
            # Wait for page load
            time.sleep(5)
            
            # Parse page
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            item_data = {
                'id': item_id,
                'name': None,
                'type': None,
                'slot': None,
                'realm': realm,
                'level': None,
                'quality': None,
                'stats': {},
                'resistances': {},
                'bonuses': {},
                'merchants': []
            }
            
            # Extract item name - try different methods
            name_elem = soup.find('h1', class_=lambda x: x and 'item' in x.lower() if x else False)
            if not name_elem:
                name_elem = soup.find('h1')
            if not name_elem:
                # Try to find in title
                title_elem = soup.find('title')
                if title_elem:
                    title_text = title_elem.get_text()
                    # Remove "Eden - " prefix if present
                    item_data['name'] = title_text.replace('Eden - ', '').strip()
            else:
                item_data['name'] = name_elem.get_text(strip=True)
            
            # Find the item info container (usually a div/table with class containing 'item')
            item_container = soup.find(['div', 'table'], class_=lambda x: x and any(c in x.lower() for c in ['item', 'detail']) if x else False)
            
            if item_container:
                container_text = item_container.get_text()
            else:
                container_text = soup.get_text()
            
            # Extract Type (Armor type, weapon type, etc.)
            type_match = re.search(r'Type:\s*([^\n\r]+)', container_text, re.IGNORECASE)
            if type_match:
                item_data['type'] = type_match.group(1).strip()
            
            # Extract Slot
            slot_match = re.search(r'Slot:\s*([^\n\r]+)', container_text, re.IGNORECASE)
            if slot_match:
                item_data['slot'] = slot_match.group(1).strip()
            
            # Extract Level
            level_match = re.search(r'Level:\s*(\d+)', container_text, re.IGNORECASE)
            if level_match:
                item_data['level'] = level_match.group(1).strip()
            
            # Extract Quality
            quality_match = re.search(r'Quality:\s*(\d+)%', container_text, re.IGNORECASE)
            if quality_match:
                item_data['quality'] = quality_match.group(1).strip()
            
            # Parse merchants section
            merchants_section = soup.find('h2', string=re.compile('From Merchants', re.IGNORECASE))
            if merchants_section:
                # Find content after the header
                merchant_content = merchants_section.find_next_sibling()
                if merchant_content:
                    merchant_text = merchant_content.get_text()
                    merchant_lines = [line.strip() for line in merchant_text.split('\n') if line.strip()]
                    
                    current_merchant = None
                    i = 0
                    while i < len(merchant_lines):
                        line = merchant_lines[i]
                        i += 1
                        
                        if not line:
                            continue
                        
                        # Check if line contains "Level:" pattern
                        if 'Level:' in line:
                            if current_merchant is None:
                                # Previous line should be merchant name
                                if i > 1:
                                    merchant_name = merchant_lines[i - 2].strip()
                                else:
                                    merchant_name = line.split('Level:')[0].strip()
                                
                                current_merchant = {
                                    'name': merchant_name,
                                    'level': line.split('Level:')[1].strip() if 'Level:' in line else '',
                                    'location': None,
                                    'zone': None,
                                    'zone_full': None,
                                    'price': None
                                }
                        
                        # Location line (starts with "in ")
                        elif line.startswith('in ') and current_merchant:
                            zone_full = line.replace('in ', '').strip()
                            zone_short = self.ZONE_MAPPING.get(zone_full, zone_full)
                            current_merchant['zone'] = zone_short
                            current_merchant['zone_full'] = zone_full
                        
                        # Location coordinates (starts with "Loc:")
                        elif line.startswith('Loc:') and current_merchant:
                            current_merchant['location'] = line.replace('Loc:', '').strip()
                        
                        # Price line (starts with "Price:")
                        elif line.startswith('Price:') and current_merchant:
                            price_text = line.replace('Price:', '').strip()
                            if not price_text and i < len(merchant_lines):
                                # Price on next line
                                price_text = merchant_lines[i].strip()
                                i += 1
                            
                            current_merchant['price'] = price_text
                            current_merchant['price_parsed'] = self.parse_price(price_text)
                            
                            # Override zone based on currency
                            if current_merchant['price_parsed']:
                                currency = current_merchant['price_parsed']['currency']
                                if currency == 'Atlantean Glass':
                                    current_merchant['zone'] = 'ToA'
                                elif currency == 'Seals':
                                    current_merchant['zone'] = 'DF'
                                elif currency == 'Roots':
                                    current_merchant['zone'] = 'Galladoria'
                            
                            # Merchant entry complete
                            if current_merchant['name']:
                                item_data['merchants'].append(current_merchant)
                            current_merchant = None
            
            return item_data
            
        except Exception as e:
            self.logger.error(f"Erreur récupération détails item: {e}", extra={"action": "MARKET"})
            return None
