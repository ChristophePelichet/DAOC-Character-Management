"""
Character Profile Scraper for Eden Herald
Specialized scraper to extract information from character profile pages.
This module does NOT modify the existing eden_scraper.py

Purpose: 
- Scrape character profile pages (Herald URL)
- Extract data from various tabs (Wealth, Stats, etc.)
- Start with Wealth tab > Money value

Author: DAOC Character Manager
Version: 0.107
"""

import logging
import time
import traceback
from pathlib import Path
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Functions.logging_manager import get_logger, log_with_action
from Functions.config_manager import config

# Create dedicated logger for character profile scraping
profile_logger = get_logger("CHARACTER_PROFILE")


class CharacterProfileScraper:
    """
    Scraper dedicated to extracting information from character profile pages.
    Does not interfere with existing EdenScraper functionality.
    """
    
    def __init__(self, cookie_manager):
        """
        Initialize the character profile scraper
        
        Args:
            cookie_manager: CookieManager instance for authentication
        """
        self.cookie_manager = cookie_manager
        self.driver = None
        
        log_with_action(profile_logger, "info", "CharacterProfileScraper initialized", action="INIT")
    
    def initialize_driver(self, headless=False):
        """
        Initialize Selenium WebDriver for profile scraping
        USES EXACT SAME METHOD AS eden_scraper.py
        
        Args:
            headless: Whether to run browser in headless mode
            
        Returns:
            bool: True if initialization successful
        """
        try:
            # EXACT SAME AS eden_scraper.py
            from Functions.config_manager import config
            preferred_browser = config.get('preferred_browser', 'Chrome')
            allow_download = config.get('allow_browser_download', False)
            
            # Use cookie_manager's browser initialization (SAME AS eden_scraper.py)
            driver, browser_name = self.cookie_manager._initialize_browser_driver(
                headless=headless,
                preferred_browser=preferred_browser,
                allow_download=allow_download
            )
            
            if driver:
                self.driver = driver
                
                # Minimize browser window if not in headless mode (SAME AS eden_scraper.py)
                if not headless:
                    try:
                        self.driver.minimize_window()
                        log_with_action(profile_logger, "info", "Browser window minimized", action="INIT")
                    except Exception as e:
                        log_with_action(profile_logger, "warning", f"Could not minimize window: {e}", action="INIT")
                
                log_with_action(profile_logger, "info", f"Driver initialized: {browser_name}", action="INIT")
                return True
            else:
                log_with_action(profile_logger, "error", "Could not initialize any browser", action="INIT")
                return False
            
        except Exception as e:
            log_with_action(profile_logger, "error", f"Failed to initialize driver: {e}", action="INIT")
            return False
    
    def load_cookies(self):
        """
        Load cookies from cookie manager into the browser
        
        Returns:
            bool: True if cookies loaded successfully and session is active
        """
        if not self.driver:
            log_with_action(profile_logger, "error", "Driver not initialized", action="LOAD_COOKIES")
            return False
        
        try:
            cookies_list = self.cookie_manager.get_cookies_for_scraper()
            if not cookies_list:
                log_with_action(profile_logger, "error", "No cookies available", action="LOAD_COOKIES")
                return False
            
            log_with_action(profile_logger, "info", f"Loading {len(cookies_list)} cookies...", action="LOAD_COOKIES")
            
            # Step 1: Navigate to homepage
            log_with_action(profile_logger, "info", "Step 1: Navigating to https://eden-daoc.net/", action="LOAD_COOKIES")
            self.driver.get("https://eden-daoc.net/")
            time.sleep(1)
            
            # Step 2: Add cookies
            log_with_action(profile_logger, "info", "Step 2: Adding cookies to browser", action="LOAD_COOKIES")
            cookies_added = 0
            for cookie in cookies_list:
                try:
                    # Remove expired cookies
                    if 'expiry' in cookie:
                        if cookie['expiry'] < time.time():
                            log_with_action(profile_logger, "debug", 
                                          f"Cookie {cookie.get('name')} expired, trying anyway", 
                                          action="LOAD_COOKIES")
                    
                    self.driver.add_cookie(cookie)
                    cookies_added += 1
                except Exception as e:
                    log_with_action(profile_logger, "warning", 
                                  f"Failed to add cookie {cookie.get('name')}: {e}", 
                                  action="LOAD_COOKIES")
            
            log_with_action(profile_logger, "info", 
                          f"Added {cookies_added}/{len(cookies_list)} cookies", 
                          action="LOAD_COOKIES")
            
            # Step 3: Refresh to activate cookies
            log_with_action(profile_logger, "info", "Step 3: Refreshing page to activate session", action="LOAD_COOKIES")
            self.driver.refresh()
            time.sleep(2)
            
            # Step 4: Navigate to Herald to test session (CRITICAL STEP)
            log_with_action(profile_logger, "info", "Step 4: Navigating to Herald to test session", action="LOAD_COOKIES")
            self.driver.get("https://eden-daoc.net/herald")
            time.sleep(2)
            
            # Check if connected
            current_url = self.driver.current_url
            html_content = self.driver.page_source
            
            log_with_action(profile_logger, "info", f"Current URL: {current_url}", action="LOAD_COOKIES")
            log_with_action(profile_logger, "info", f"HTML size: {len(html_content)} chars", action="LOAD_COOKIES")
            
            # Detection: If we have "not available" message → Not connected
            error_message = 'The requested page "herald" is not available.'
            has_error = error_message in html_content
            
            log_with_action(profile_logger, "info", f"Error message present: {has_error}", action="LOAD_COOKIES")
            
            if has_error:
                log_with_action(profile_logger, "error", 
                              'NOT CONNECTED - Herald page not available', 
                              action="LOAD_COOKIES")
                log_with_action(profile_logger, "error", 
                              'Please regenerate cookies using Cookie Manager', 
                              action="LOAD_COOKIES")
                return False
            else:
                log_with_action(profile_logger, "info", 
                              "Successfully connected to Herald", 
                              action="LOAD_COOKIES")
                return True
            
        except Exception as e:
            log_with_action(profile_logger, "error", f"Failed to load cookies: {e}", action="LOAD_COOKIES")
            return False
    
    def scrape_wealth_money(self, character_url):
        """
        Scrape the Money value from the Wealth tab of a character profile
        Uses the same method as search_herald_character in eden_scraper.py
        
        Args:
            character_url: Full URL to character profile (e.g., https://eden-daoc.net/herald?n=player&k=CharName)
            
        Returns:
            dict: {
                'success': bool,
                'money': str or None,  # Money value as string (e.g., "1234g 56s 78c")
                'error': str or None
            }
        """
        if not self.driver:
            return {
                'success': False,
                'money': None,
                'error': 'Driver not initialized'
            }
        
        try:
            # Ensure URL includes wealth tab parameter
            if 't=wealth' not in character_url:
                if '?' in character_url:
                    character_url += '&t=wealth'
                else:
                    character_url += '?t=wealth'
            
            log_with_action(profile_logger, "info", 
                          f"Navigating to: {character_url}", 
                          action="SCRAPE_WEALTH")
            
            # Navigate to character wealth page (SAME AS eden_scraper.py does for search)
            self.driver.get(character_url)
            
            # Wait for page to fully load (SAME AS search: 5 seconds)
            log_with_action(profile_logger, "info", 
                          "Waiting for page to fully load (5 seconds)...", 
                          action="SCRAPE_WEALTH")
            time.sleep(5)
            
            # Extract HTML content (SAME AS search)
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            log_with_action(profile_logger, "info", 
                          f"Page loaded - Size: {len(page_source)} chars", 
                          action="SCRAPE_WEALTH")
            
            # Check if we got the error message (not connected)
            if 'The requested page "herald" is not available.' in page_source:
                log_with_action(profile_logger, "error", 
                              "Not connected - Herald page not available", 
                              action="SCRAPE_WEALTH")
                return {
                    'success': False,
                    'money': None,
                    'error': 'Not connected to Herald - please regenerate cookies'
                }
            
            # Look for the player_content div (SAME AS search looks for tables)
            player_content = soup.find('div', id='player_content')
            
            if not player_content:
                log_with_action(profile_logger, "warning", "player_content div not found", action="SCRAPE_WEALTH")
                return {
                    'success': False,
                    'money': None,
                    'error': 'Player content not loaded'
                }
            
            # Search for Money in tables
            # Herald typically uses table structures
            money_value = None
            
            # Look for text containing "Money" followed by value
            for element in player_content.find_all(['td', 'div', 'span']):
                text = element.get_text(strip=True)
                if 'Money' in text or 'money' in text:
                    # Pattern 1: <td>Money</td><td>1234g 56s 78c</td>
                    next_sibling = element.find_next_sibling()
                    if next_sibling:
                        value = next_sibling.get_text(strip=True)
                        # Check if value looks like money (contains g, s, or c)
                        if any(char in value.lower() for char in ['g', 's', 'c']) or value.isdigit():
                            money_value = value
                            break
                    
                    # Pattern 2: <td>Money: 1234g 56s 78c</td>
                    if ':' in text:
                        parts = text.split(':', 1)
                        if len(parts) == 2:
                            value = parts[1].strip()
                            if any(char in value.lower() for char in ['g', 's', 'c']) or value.isdigit():
                                money_value = value
                                break
            
            if money_value:
                log_with_action(profile_logger, "info", f"Money found: {money_value}", action="SCRAPE_WEALTH")
                return {
                    'success': True,
                    'money': money_value,
                    'error': None
                }
            else:
                log_with_action(profile_logger, "warning", "Money value not found on page", action="SCRAPE_WEALTH")
                
                return {
                    'success': False,
                    'money': None,
                    'error': 'Money value not found'
                }
            
        except Exception as e:
            error_msg = f"Error scraping wealth: {str(e)}"
            log_with_action(profile_logger, "error", f"{error_msg}\n{traceback.format_exc()}", action="SCRAPE_WEALTH")
            return {
                'success': False,
                'money': None,
                'error': error_msg
            }
    
    def close(self):
        """Close the WebDriver cleanly"""
        if self.driver:
            try:
                self.driver.quit()
                log_with_action(profile_logger, "info", "Driver closed", action="CLEANUP")
            except Exception as e:
                log_with_action(profile_logger, "warning", f"Error closing driver: {e}", action="CLEANUP")
            finally:
                self.driver = None
    
    def scrape_rvr_captures(self, character_url):
        """
        Scrape RvR capture statistics from the Characters tab (default view)
        
        Args:
            character_url: Full URL to character profile (e.g., https://eden-daoc.net/herald?n=player&k=CharName)
            
        Returns:
            dict: {
                'success': bool,
                'tower_captures': int or None,
                'keep_captures': int or None,
                'relic_captures': int or None,
                'error': str or None
            }
        """
        if not self.driver:
            return {
                'success': False,
                'tower_captures': None,
                'keep_captures': None,
                'relic_captures': None,
                'error': 'Driver not initialized'
            }
        
        try:
            # Remove any tab parameter to get default Characters tab
            base_url = character_url.split('&t=')[0].split('?t=')[0]
            
            log_with_action(profile_logger, "info", 
                          f"Navigating to: {base_url}", 
                          action="SCRAPE_RVR")
            
            # Navigate to character page (default Characters tab)
            self.driver.get(base_url)
            
            # Wait for page to fully load
            log_with_action(profile_logger, "info", 
                          "Waiting for page to fully load (5 seconds)...", 
                          action="SCRAPE_RVR")
            time.sleep(5)
            
            # Extract HTML content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            log_with_action(profile_logger, "info", 
                          f"Page loaded - Size: {len(page_source)} chars", 
                          action="SCRAPE_RVR")
            
            # Check if we got the error message (not connected)
            if 'The requested page "herald" is not available.' in page_source:
                log_with_action(profile_logger, "error", 
                              "Not connected - Herald page not available", 
                              action="SCRAPE_RVR")
                return {
                    'success': False,
                    'tower_captures': None,
                    'keep_captures': None,
                    'relic_captures': None,
                    'error': 'Not connected to Herald - please regenerate cookies'
                }
            
            # Look for the player_content div
            player_content = soup.find('div', id='player_content')
            
            if not player_content:
                log_with_action(profile_logger, "warning", "player_content div not found", action="SCRAPE_RVR")
                return {
                    'success': False,
                    'tower_captures': None,
                    'keep_captures': None,
                    'relic_captures': None,
                    'error': 'Player content not loaded'
                }
            
            # Helper function to clean number strings
            def clean_number(text):
                """Remove thousand separators (spaces, commas, non-breaking spaces) from number string"""
                return text.replace(',', '').replace(' ', '').replace('\xa0', '')
            
            # Search for RvR statistics in table cells
            result = {
                'success': False,
                'tower_captures': None,
                'keep_captures': None,
                'relic_captures': None,
                'error': None
            }
            
            # Search for RvR statistics in table cells
            # Structure: <td>Label</td><td>Value</td>
            all_cells = player_content.find_all('td')
            
            for i, cell in enumerate(all_cells):
                cell_text = cell.get_text(strip=True)
                
                # Check if this is a label cell
                if 'Relic Captures' in cell_text:
                    # Next cell should contain the value
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['relic_captures'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Relic Captures: {result['relic_captures']}", 
                                          action="SCRAPE_RVR")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Relic Captures value: {value_text}", 
                                          action="SCRAPE_RVR")
                
                elif 'Keep Captures' in cell_text:
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['keep_captures'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Keep Captures: {result['keep_captures']}", 
                                          action="SCRAPE_RVR")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Keep Captures value: {value_text}", 
                                          action="SCRAPE_RVR")
                
                elif 'Tower Captures' in cell_text:
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['tower_captures'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Tower Captures: {result['tower_captures']}", 
                                          action="SCRAPE_RVR")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Tower Captures value: {value_text}", 
                                          action="SCRAPE_RVR")
            
            # Check if we found all values
            if result['tower_captures'] is not None and \
               result['keep_captures'] is not None and \
               result['relic_captures'] is not None:
                result['success'] = True
                log_with_action(profile_logger, "info", 
                              f"Successfully extracted RvR stats: T={result['tower_captures']}, K={result['keep_captures']}, R={result['relic_captures']}", 
                              action="SCRAPE_RVR")
            else:
                result['error'] = 'Some RvR statistics not found'
                log_with_action(profile_logger, "warning", 
                              f"Incomplete RvR data: {result}", 
                              action="SCRAPE_RVR")
            
            return result
            
        except Exception as e:
            error_msg = f"Error scraping RvR captures: {e}"
            log_with_action(profile_logger, "error", error_msg, action="SCRAPE_RVR")
            return {
                'success': False,
                'tower_captures': None,
                'keep_captures': None,
                'relic_captures': None,
                'error': error_msg
            }
    
    def scrape_pvp_stats(self, character_url):
        """
        Scrape PvP statistics from the PvP tab
        
        Args:
            character_url: Full URL to character profile (e.g., https://eden-daoc.net/herald?n=player&k=CharName)
            
        Returns:
            dict: {
                'success': bool,
                'solo_kills': int or None,
                'solo_kills_alb': int or None,
                'solo_kills_hib': int or None,
                'solo_kills_mid': int or None,
                'deathblows': int or None,
                'deathblows_alb': int or None,
                'deathblows_hib': int or None,
                'deathblows_mid': int or None,
                'kills': int or None,
                'kills_alb': int or None,
                'kills_hib': int or None,
                'kills_mid': int or None,
                'error': str or None
            }
        """
        def clean_number(text):
            """Remove thousand separators (spaces, commas, non-breaking spaces) from number string"""
            return text.replace(',', '').replace(' ', '').replace('\xa0', '')
        
        if not self.driver:
            return {
                'success': False,
                'solo_kills': None, 'solo_kills_alb': None, 'solo_kills_hib': None, 'solo_kills_mid': None,
                'deathblows': None, 'deathblows_alb': None, 'deathblows_hib': None, 'deathblows_mid': None,
                'kills': None, 'kills_alb': None, 'kills_hib': None, 'kills_mid': None,
                'error': 'Driver not initialized'
            }
        
        try:
            # Ensure URL includes PvP tab parameter
            base_url = character_url.split('&t=')[0].split('?t=')[0]
            pvp_url = f"{base_url}&t=pvp" if '?' in base_url else f"{base_url}?t=pvp"
            
            log_with_action(profile_logger, "info", 
                          f"Navigating to PvP tab: {pvp_url}", 
                          action="SCRAPE_PVP")
            
            # Navigate to PvP tab
            self.driver.get(pvp_url)
            
            # Wait for page to fully load
            log_with_action(profile_logger, "info", 
                          "Waiting for page to fully load (5 seconds)...", 
                          action="SCRAPE_PVP")
            time.sleep(5)
            
            # Extract HTML content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            log_with_action(profile_logger, "info", 
                          f"Page loaded - Size: {len(page_source)} chars", 
                          action="SCRAPE_PVP")
            
            # Check if we got the error message (not connected)
            if 'The requested page "herald" is not available.' in page_source:
                log_with_action(profile_logger, "error", 
                              "Not connected - Herald page not available", 
                              action="SCRAPE_PVP")
                return {
                    'success': False,
                    'solo_kills': None, 'solo_kills_alb': None, 'solo_kills_hib': None, 'solo_kills_mid': None,
                    'deathblows': None, 'deathblows_alb': None, 'deathblows_hib': None, 'deathblows_mid': None,
                    'kills': None, 'kills_alb': None, 'kills_hib': None, 'kills_mid': None,
                    'error': 'Not connected to Herald - please regenerate cookies'
                }
            
            # Look for the player_content div
            player_content = soup.find('div', id='player_content')
            
            if not player_content:
                log_with_action(profile_logger, "warning", "player_content div not found", action="SCRAPE_PVP")
                return {
                    'success': False,
                    'solo_kills': None, 'solo_kills_alb': None, 'solo_kills_hib': None, 'solo_kills_mid': None,
                    'deathblows': None, 'deathblows_alb': None, 'deathblows_hib': None, 'deathblows_mid': None,
                    'kills': None, 'kills_alb': None, 'kills_hib': None, 'kills_mid': None,
                    'error': 'Player content not loaded'
                }
            
            # Initialize results
            result = {
                'success': False,
                'solo_kills': None, 'solo_kills_alb': None, 'solo_kills_hib': None, 'solo_kills_mid': None,
                'deathblows': None, 'deathblows_alb': None, 'deathblows_hib': None, 'deathblows_mid': None,
                'kills': None, 'kills_alb': None, 'kills_hib': None, 'kills_mid': None,
                'error': None
            }
            
            # Search for PvP statistics in table cells
            # Structure: <td>Label</td> <td>Empty</td> <td>Albion</td> <td>Hibernia</td> <td>Midgard</td> <td>All</td>
            all_cells = player_content.find_all('td')
            
            for i, cell in enumerate(all_cells):
                cell_text = cell.get_text(strip=True)
                cell_class = cell.get('class', [])
                
                # Check if this is a label cell
                if 'allbg2' in cell_class and 'med' in cell_class and 'bold' in cell_class:
                    if cell_text == 'Solo Kills':
                        # Extract values: +1=Empty, +2=Alb, +3=Hib, +4=Mid, +5=All
                        if i + 5 < len(all_cells):
                            try:
                                result['solo_kills_alb'] = int(clean_number(all_cells[i + 2].get_text(strip=True)))
                                result['solo_kills_hib'] = int(clean_number(all_cells[i + 3].get_text(strip=True)))
                                result['solo_kills_mid'] = int(clean_number(all_cells[i + 4].get_text(strip=True)))
                                result['solo_kills'] = int(clean_number(all_cells[i + 5].get_text(strip=True)))
                                log_with_action(profile_logger, "info", 
                                              f"Solo Kills: Total={result['solo_kills']}, Alb={result['solo_kills_alb']}, Hib={result['solo_kills_hib']}, Mid={result['solo_kills_mid']}", 
                                              action="SCRAPE_PVP")
                            except (ValueError, IndexError) as e:
                                log_with_action(profile_logger, "warning", f"Could not parse Solo Kills: {e}", action="SCRAPE_PVP")
                    
                    elif cell_text == 'Deathblows':
                        if i + 5 < len(all_cells):
                            try:
                                result['deathblows_alb'] = int(clean_number(all_cells[i + 2].get_text(strip=True)))
                                result['deathblows_hib'] = int(clean_number(all_cells[i + 3].get_text(strip=True)))
                                result['deathblows_mid'] = int(clean_number(all_cells[i + 4].get_text(strip=True)))
                                result['deathblows'] = int(clean_number(all_cells[i + 5].get_text(strip=True)))
                                log_with_action(profile_logger, "info", 
                                              f"Deathblows: Total={result['deathblows']}, Alb={result['deathblows_alb']}, Hib={result['deathblows_hib']}, Mid={result['deathblows_mid']}", 
                                              action="SCRAPE_PVP")
                            except (ValueError, IndexError) as e:
                                log_with_action(profile_logger, "warning", f"Could not parse Deathblows: {e}", action="SCRAPE_PVP")
                    
                    elif cell_text == 'Kills':
                        if i + 5 < len(all_cells):
                            try:
                                result['kills_alb'] = int(clean_number(all_cells[i + 2].get_text(strip=True)))
                                result['kills_hib'] = int(clean_number(all_cells[i + 3].get_text(strip=True)))
                                result['kills_mid'] = int(clean_number(all_cells[i + 4].get_text(strip=True)))
                                result['kills'] = int(clean_number(all_cells[i + 5].get_text(strip=True)))
                                log_with_action(profile_logger, "info", 
                                              f"Kills: Total={result['kills']}, Alb={result['kills_alb']}, Hib={result['kills_hib']}, Mid={result['kills_mid']}", 
                                              action="SCRAPE_PVP")
                            except (ValueError, IndexError) as e:
                                log_with_action(profile_logger, "warning", f"Could not parse Kills: {e}", action="SCRAPE_PVP")
            
            # Check if we found all values (at least the totals)
            missing_stats = []
            if result['solo_kills'] is None:
                missing_stats.append('Solo Kills')
            if result['deathblows'] is None:
                missing_stats.append('Deathblows')
            if result['kills'] is None:
                missing_stats.append('Kills')
            
            if not missing_stats:
                result['success'] = True
                log_with_action(profile_logger, "info", 
                              "Successfully extracted PvP stats with realm breakdown", 
                              action="SCRAPE_PVP")
            else:
                result['error'] = f"PvP statistics not found: {', '.join(missing_stats)}"
                log_with_action(profile_logger, "warning", 
                              f"Incomplete PvP data - missing: {', '.join(missing_stats)}", 
                              action="SCRAPE_PVP")
                
                # Debug: Save HTML for analysis if stats are missing
                try:
                    debug_file = Path(__file__).parent.parent / "debug_pvp_missing.html"
                    debug_file.write_text(page_source, encoding='utf-8')
                    log_with_action(profile_logger, "info", 
                                  f"Saved debug HTML to {debug_file}", 
                                  action="SCRAPE_PVP")
                except Exception as debug_error:
                    log_with_action(profile_logger, "warning", 
                                  f"Could not save debug HTML: {debug_error}", 
                                  action="SCRAPE_PVP")
            
            return result
            
        except Exception as e:
            error_msg = f"Error scraping PvP stats: {e}"
            log_with_action(profile_logger, "error", error_msg, action="SCRAPE_PVP")
            return {
                'success': False,
                'solo_kills': None, 'solo_kills_alb': None, 'solo_kills_hib': None, 'solo_kills_mid': None,
                'deathblows': None, 'deathblows_alb': None, 'deathblows_hib': None, 'deathblows_mid': None,
                'kills': None, 'kills_alb': None, 'kills_hib': None, 'kills_mid': None,
                'error': error_msg
            }

    def scrape_pve_stats(self, character_url):
        """
        Scrape PvE statistics from character profile
        
        Args:
            character_url: Character profile URL (e.g., https://eden-daoc.net/herald?n=player&k=XXX)
            
        Returns:
            dict: PvE statistics
        """
        if not self.driver:
            return {
                'success': False,
                'error': 'Driver not initialized'
            }
        
        try:
            # Ensure URL includes PvE tab parameter
            base_url = character_url.split('&t=')[0].split('?t=')[0]
            pve_url = f"{base_url}&t=pve" if '?' in base_url else f"{base_url}?t=pve"
            
            log_with_action(profile_logger, "info", 
                          f"Navigating to PvE tab: {pve_url}", 
                          action="SCRAPE_PVE")
            
            # Navigate to PvE tab
            self.driver.get(pve_url)
            
            # Wait for page to fully load
            log_with_action(profile_logger, "info", 
                          "Waiting for page to fully load (5 seconds)...", 
                          action="SCRAPE_PVE")
            time.sleep(5)
            
            # Extract HTML content
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            log_with_action(profile_logger, "info", 
                          f"Page loaded - Size: {len(page_source)} chars", 
                          action="SCRAPE_PVE")
            
            # Check if we got the error message (not connected)
            if 'The requested page "herald" is not available.' in page_source:
                log_with_action(profile_logger, "error", 
                              "Not connected - Herald page not available", 
                              action="SCRAPE_PVE")
                return {
                    'success': False,
                    'error': 'Not connected to Herald - please regenerate cookies'
                }
            
            # Look for the player_content div
            player_content = soup.find('div', id='player_content')
            
            if not player_content:
                log_with_action(profile_logger, "warning", "player_content div not found", action="SCRAPE_PVE")
                return {
                    'success': False,
                    'dragon_kills': None,
                    'legion_kills': None,
                    'mini_dragon_kills': None,
                    'epic_encounters': None,
                    'epic_dungeons': None,
                    'sobekite': None,
                    'error': 'Player content not loaded'
                }
            
            # Helper function to clean number strings
            def clean_number(text):
                """Remove thousand separators (spaces, commas, non-breaking spaces) from number string"""
                return text.replace(',', '').replace(' ', '').replace('\xa0', '')
            
            # Search for PvE statistics table
            result = {
                'success': False,
                'dragon_kills': None,
                'legion_kills': None,
                'mini_dragon_kills': None,
                'epic_encounters': None,
                'epic_dungeons': None,
                'sobekite': None,
                'error': None
            }
            
            # Find the PvE stats table (class="pvestats")
            pve_table = player_content.find('table', class_='pvestats')
            
            if not pve_table:
                log_with_action(profile_logger, "warning", "pvestats table not found", action="SCRAPE_PVE")
                result['error'] = 'PvE stats table not found'
                return result
            
            # Find all table cells in pvestats table only
            all_cells = pve_table.find_all('td')
            
            for i, cell in enumerate(all_cells):
                cell_text = cell.get_text(strip=True)
                
                # Only process cells with 'bold' class (these are the labels)
                if 'bold' not in cell.get('class', []):
                    continue
                
                # Check for each PvE stat
                if cell_text == 'Dragon Kills':
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['dragon_kills'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Dragon Kills: {result['dragon_kills']}", 
                                          action="SCRAPE_PVE")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Dragon Kills value: {value_text}", 
                                          action="SCRAPE_PVE")
                
                elif cell_text == 'Legion Kills':
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['legion_kills'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Legion Kills: {result['legion_kills']}", 
                                          action="SCRAPE_PVE")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Legion Kills value: {value_text}", 
                                          action="SCRAPE_PVE")
                
                elif cell_text == 'Mini Dragon Kills':
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['mini_dragon_kills'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Mini Dragon Kills: {result['mini_dragon_kills']}", 
                                          action="SCRAPE_PVE")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Mini Dragon Kills value: {value_text}", 
                                          action="SCRAPE_PVE")
                
                elif cell_text == 'Epic Encounters':
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['epic_encounters'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Epic Encounters: {result['epic_encounters']}", 
                                          action="SCRAPE_PVE")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Epic Encounters value: {value_text}", 
                                          action="SCRAPE_PVE")
                
                elif cell_text == 'Epic Dungeons':
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['epic_dungeons'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Epic Dungeons: {result['epic_dungeons']}", 
                                          action="SCRAPE_PVE")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Epic Dungeons value: {value_text}", 
                                          action="SCRAPE_PVE")
                
                elif cell_text == 'Sobekite':
                    if i + 1 < len(all_cells):
                        value_text = all_cells[i + 1].get_text(strip=True)
                        try:
                            result['sobekite'] = int(clean_number(value_text))
                            log_with_action(profile_logger, "info", 
                                          f"Found Sobekite: {result['sobekite']}", 
                                          action="SCRAPE_PVE")
                        except ValueError:
                            log_with_action(profile_logger, "warning", 
                                          f"Could not parse Sobekite value: {value_text}", 
                                          action="SCRAPE_PVE")
            
            # Check if we found all values
            missing_stats = []
            if result['dragon_kills'] is None:
                missing_stats.append('Dragon Kills')
            if result['legion_kills'] is None:
                missing_stats.append('Legion Kills')
            if result['mini_dragon_kills'] is None:
                missing_stats.append('Mini Dragon Kills')
            if result['epic_encounters'] is None:
                missing_stats.append('Epic Encounters')
            if result['epic_dungeons'] is None:
                missing_stats.append('Epic Dungeons')
            if result['sobekite'] is None:
                missing_stats.append('Sobekite')
            
            if not missing_stats:
                result['success'] = True
                log_with_action(profile_logger, "info", 
                              "Successfully extracted all PvE stats", 
                              action="SCRAPE_PVE")
            else:
                result['error'] = f"PvE statistics not found: {', '.join(missing_stats)}"
                log_with_action(profile_logger, "warning", 
                              f"Incomplete PvE data - missing: {', '.join(missing_stats)}", 
                              action="SCRAPE_PVE")
                
                # Debug: Save HTML for analysis if stats are missing
                try:
                    debug_file = Path(__file__).parent.parent / "debug_pve_missing.html"
                    debug_file.write_text(page_source, encoding='utf-8')
                    log_with_action(profile_logger, "info", 
                                  f"Saved debug HTML to {debug_file}", 
                                  action="SCRAPE_PVE")
                except Exception as debug_error:
                    log_with_action(profile_logger, "warning", 
                                  f"Could not save debug HTML: {debug_error}", 
                                  action="SCRAPE_PVE")
            
            return result
            
        except Exception as e:
            error_msg = f"Error scraping PvE stats: {e}"
            log_with_action(profile_logger, "error", error_msg, action="SCRAPE_PVE")
            return {
                'success': False,
                'error': error_msg
            }
    
    def scrape_achievements(self, character_url):
        """
        Scrape achievements from character Herald page.
        
        Args:
            character_url (str): URL of the character Herald page
            
        Returns:
            dict: {
                'success': bool,
                'achievements': list of dict with 'title' and 'progress' (e.g., "19/50"),
                'error': str or None
            }
        """
        try:
            log_with_action(profile_logger, "info", 
                          f"Starting achievements scraping for URL: {character_url}", 
                          action="SCRAPE_ACHIEVEMENTS")
            
            # Navigate to Achievements tab (accessed via &t=achievements parameter)
            if '&t=' in character_url:
                achievements_url = character_url
            else:
                achievements_url = f"{character_url}&t=achievements"
            
            log_with_action(profile_logger, "info", 
                          f"Loading achievements URL: {achievements_url}", 
                          action="SCRAPE_ACHIEVEMENTS")
            
            self.driver.get(achievements_url)
            
            # Wait for page to load
            import time
            time.sleep(2)
            
            # Check if connected
            page_source = self.driver.page_source
            
            if 'The requested page "herald" is not available.' in page_source:
                log_with_action(profile_logger, "error", 
                              "Not connected - Herald page not available", 
                              action="SCRAPE_ACHIEVEMENTS")
                return {
                    'success': False,
                    'achievements': [],
                    'error': 'Not connected to Herald - please regenerate cookies'
                }
            
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find player_content div
            player_content = soup.find('div', id='player_content')
            
            if not player_content:
                log_with_action(profile_logger, "warning", 
                              "player_content div not found", 
                              action="SCRAPE_ACHIEVEMENTS")
                return {
                    'success': False,
                    'achievements': [],
                    'error': 'Player content not loaded'
                }
            
            achievements_list = []
            
            # Find all table rows with class "titlerow" - these contain the achievements
            # Structure: <tr class="titlerow"><td>Title</td><td>X / Y</td></tr>
            # Note: "Current:" rows show the current achievement tier name
            titlerows = player_content.find_all('tr', class_='titlerow')
            
            log_with_action(profile_logger, "info", 
                          f"Found {len(titlerows)} titlerow elements", 
                          action="SCRAPE_ACHIEVEMENTS")
            
            i = 0
            while i < len(titlerows):
                row = titlerows[i]
                cells = row.find_all('td')
                
                if len(cells) >= 2:
                    title = cells[0].get_text(strip=True)
                    progress = cells[1].get_text(strip=True)
                    
                    # If this is "Current:", combine it with the tier name
                    if title == "Current:":
                        # Format as "Current: Tier Name"
                        current_tier = progress if progress != "-" else "None"
                        # Add to the previous achievement if it exists
                        if achievements_list:
                            achievements_list[-1]['current'] = current_tier
                    else:
                        # Regular achievement with progress
                        if title and progress:
                            achievements_list.append({
                                'title': title,
                                'progress': progress,
                                'current': None  # Will be filled by next "Current:" row if exists
                            })
                            
                            log_with_action(profile_logger, "info", 
                                          f"Achievement found: {title} - {progress}", 
                                          action="SCRAPE_ACHIEVEMENTS")
                
                i += 1
            
            log_with_action(profile_logger, "info", 
                          f"Achievements scraping completed: {len(achievements_list)} achievements found", 
                          action="SCRAPE_ACHIEVEMENTS")
            
            return {
                'success': True,
                'achievements': achievements_list,
                'error': None
            }
            
        except Exception as e:
            error_msg = f"Error scraping achievements: {e}"
            log_with_action(profile_logger, "error", 
                          f"{error_msg}\n{traceback.format_exc()}", 
                          action="SCRAPE_ACHIEVEMENTS")
            return {
                'success': False,
                'achievements': [],
                'error': error_msg
            }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure cleanup"""
        self.close()


