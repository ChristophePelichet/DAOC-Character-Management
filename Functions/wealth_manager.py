"""
Wealth Manager - Retrieve and manage money information per realm
Uses the CharacterProfileScraper to get wealth data from character profiles

Version: 0.107
"""

import json
import os
from pathlib import Path
from Functions.character_profile_scraper import CharacterProfileScraper
from Functions.cookie_manager import CookieManager
from Functions.logging_manager import get_logger, log_with_action

wealth_logger = get_logger("WEALTH")

# Realm mapping
REALMS = {
    'Albion': 'alb',
    'Midgard': 'mid',
    'Hibernia': 'hib'
}


def get_first_character_per_realm(character_folder):
    """
    Get the first available character for each realm
    
    Args:
        character_folder: Path to Characters folder
        
    Returns:
        dict: {
            'Albion': {'name': str, 'url': str} or None,
            'Midgard': {'name': str, 'url': str} or None,
            'Hibernia': {'name': str, 'url': str} or None
        }
    """
    result = {
        'Albion': None,
        'Midgard': None,
        'Hibernia': None
    }
    
    if not character_folder or not os.path.exists(character_folder):
        log_with_action(wealth_logger, "warning", "Character folder not found", action="GET_CHARS")
        return result
    
    try:
        # Browse through seasons and realms
        char_path = Path(character_folder)
        
        # Get all season directories and sort them (S3, S2, S1, etc.)
        season_dirs = [d for d in char_path.iterdir() 
                      if d.is_dir() and not d.name.startswith('.')]
        # Sort by season number (descending) to get most recent first
        season_dirs.sort(key=lambda x: x.name, reverse=True)
        
        for season_dir in season_dirs:
            for realm_dir in season_dir.iterdir():
                if not realm_dir.is_dir() or realm_dir.name.startswith('.'):
                    continue
                
                realm_name = realm_dir.name
                if realm_name not in result:
                    continue
                
                # If we already have a character for this realm, skip
                if result[realm_name] is not None:
                    continue
                
                # Find first character JSON file with level >= 11
                for char_file in realm_dir.glob('*.json'):
                    try:
                        with open(char_file, 'r', encoding='utf-8') as f:
                            char_data = json.load(f)
                        
                        name = char_data.get('name')
                        url = char_data.get('url')
                        level = char_data.get('level', '0')
                        
                        # Convert level to int (handle non-numeric gracefully)
                        try:
                            char_level = int(level)
                        except (ValueError, TypeError):
                            char_level = 0
                        
                        # Only use characters level 11+ (out of tutorial)
                        if name and url and char_level >= 11:
                            result[realm_name] = {
                                'name': name,
                                'url': url
                            }
                            log_with_action(wealth_logger, "info", 
                                          f"{realm_name}: Found {name} (level {char_level})", 
                                          action="GET_CHARS")
                            break  # Found first valid character for this realm
                        elif name and char_level < 11:
                            log_with_action(wealth_logger, "debug", 
                                          f"{realm_name}: Skipping {name} (level {char_level} < 11)", 
                                          action="GET_CHARS")
                    except Exception as e:
                        log_with_action(wealth_logger, "warning", 
                                      f"Error reading {char_file}: {e}", 
                                      action="GET_CHARS")
                        continue
        
        return result
        
    except Exception as e:
        log_with_action(wealth_logger, "error", 
                       f"Error getting characters per realm: {e}", 
                       action="GET_CHARS")
        return result


def get_realm_money(character_folder, cookie_manager=None, headless=False):
    """
    Get money values for each realm
    
    Args:
        character_folder: Path to Characters folder
        cookie_manager: CookieManager instance (optional, will create if None)
        headless: Run browser in headless mode (default: False for better compatibility)
        
    Returns:
        dict: {
            'Albion': str (money value or "0"),
            'Midgard': str (money value or "0"),
            'Hibernia': str (money value or "0"),
            'success': bool,
            'errors': list of error messages
        }
    """
    result = {
        'Albion': '0',
        'Midgard': '0',
        'Hibernia': '0',
        'success': False,
        'errors': []
    }
    
    scraper = None
    
    try:
        # Get first character per realm
        characters = get_first_character_per_realm(character_folder)
        
        # Check if we have at least one character
        has_character = any(char is not None for char in characters.values())
        if not has_character:
            log_with_action(wealth_logger, "warning", 
                          "No characters found in any realm", 
                          action="GET_MONEY")
            result['errors'].append("No characters found")
            return result
        
        # Initialize cookie manager if needed
        if cookie_manager is None:
            cookie_manager = CookieManager()
        
        # Check cookies
        if not cookie_manager.cookie_exists():
            log_with_action(wealth_logger, "error", 
                          "No cookies found", 
                          action="GET_MONEY")
            result['errors'].append("No cookies available")
            return result
        
        # Initialize scraper
        scraper = CharacterProfileScraper(cookie_manager)
        
        if not scraper.initialize_driver(headless=headless):
            log_with_action(wealth_logger, "error", 
                          "Failed to initialize scraper driver", 
                          action="GET_MONEY")
            result['errors'].append("Failed to initialize browser")
            return result
        
        if not scraper.load_cookies():
            log_with_action(wealth_logger, "error", 
                          "Failed to load cookies", 
                          action="GET_MONEY")
            result['errors'].append("Failed to load cookies")
            return result
        
        # Scrape money for each realm
        for realm_name, char_info in characters.items():
            if char_info is None:
                log_with_action(wealth_logger, "info", 
                              f"{realm_name}: No character, keeping 0", 
                              action="GET_MONEY")
                continue
            
            char_name = char_info['name']
            char_url = char_info['url']
            
            log_with_action(wealth_logger, "info", 
                          f"{realm_name}: Scraping {char_name}", 
                          action="GET_MONEY")
            
            money_result = scraper.scrape_wealth_money(char_url)
            
            if money_result['success'] and money_result['money']:
                result[realm_name] = money_result['money']
                log_with_action(wealth_logger, "info", 
                              f"{realm_name}: Money = {money_result['money']}", 
                              action="GET_MONEY")
            else:
                error_msg = money_result.get('error', 'Unknown error')
                log_with_action(wealth_logger, "warning", 
                              f"{realm_name}: Failed to get money - {error_msg}", 
                              action="GET_MONEY")
                result['errors'].append(f"{realm_name}: {error_msg}")
        
        result['success'] = True
        return result
        
    except Exception as e:
        error_msg = f"Error getting realm money: {e}"
        log_with_action(wealth_logger, "error", error_msg, action="GET_MONEY")
        result['errors'].append(error_msg)
        return result
        
    finally:
        if scraper:
            scraper.close()
