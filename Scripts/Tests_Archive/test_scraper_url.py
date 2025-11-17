#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script pour scraper une URL Eden avec le EdenScraper
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Functions.eden_scraper import EdenScraper
from Functions.cookie_manager import CookieManager
from Functions.config_manager import config

def test_scrape_url(url):
    """Test scraping d'une URL spécifique"""
    print("=" * 80)
    print(f"TEST SCRAPING URL: {url}")
    print("=" * 80)
    
    # Initialize cookie manager
    print("\n1. Initialisation du Cookie Manager...")
    cookie_manager = CookieManager()
    
    # Initialize scraper
    print("\n2. Initialisation du Scraper Eden...")
    scraper = EdenScraper(cookie_manager)
    
    # Initialize driver (headless mode)
    print("\n3. Initialisation du driver Selenium (mode VISIBLE)...")
    if not scraper.initialize_driver(headless=False):
        print("❌ ERREUR: Impossible d'initialiser le driver")
        return
    
    print("✅ Driver initialisé")
    
    # Load cookies
    print("\n4. Chargement des cookies...")
    if not scraper.load_cookies():
        print("❌ ERREUR: Impossible de charger les cookies")
        scraper.close()
        return
    
    print("✅ Cookies chargés")
    
    # Navigate to URL
    print(f"\n5. Navigation vers {url}...")
    try:
        scraper.driver.get(url)
        
        # Wait for page load
        import time
        time.sleep(3)
        
        # Get page source
        html_content = scraper.driver.page_source
        current_url = scraper.driver.current_url
        
        print(f"\n✅ Page chargée")
        print(f"URL actuelle: {current_url}")
        print(f"Taille HTML: {len(html_content)} caractères")
        
        # Parse with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract interesting data
        print("\n" + "=" * 80)
        print("CONTENU DE LA PAGE:")
        print("=" * 80)
        
        # Title
        title = soup.find('title')
        if title:
            print(f"\n📄 TITRE: {title.get_text(strip=True)}")
        
        # Main content
        print("\n📋 CONTENU PRINCIPAL:\n")
        
        # Look for common elements
        main_content = soup.find('main') or soup.find('div', class_='content') or soup.body
        
        if main_content:
            # Get text content (limited to first 2000 chars)
            text_content = main_content.get_text(separator='\n', strip=True)
            print(text_content[:2000])
            
            if len(text_content) > 2000:
                print(f"\n... (contenu tronqué, {len(text_content)} caractères au total)")
        
        # Look for specific elements (tables, forms, etc.)
        print("\n" + "=" * 80)
        print("ÉLÉMENTS STRUCTURELS:")
        print("=" * 80)
        
        tables = soup.find_all('table')
        print(f"\n📊 Tables trouvées: {len(tables)}")
        
        forms = soup.find_all('form')
        print(f"📝 Formulaires trouvés: {len(forms)}")
        
        links = soup.find_all('a')
        print(f"🔗 Liens trouvés: {len(links)}")
        
        # Check for item-specific elements
        items = soup.find_all(class_=lambda x: x and 'item' in x.lower())
        print(f"🎒 Éléments 'item' trouvés: {len(items)}")
        
        # Save HTML to file for inspection
        debug_file = project_root / 'Logs' / 'debug_market_page.html'
        debug_file.parent.mkdir(exist_ok=True)
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\n💾 HTML sauvegardé dans: {debug_file}")
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du scraping: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close driver
        print("\n6. Fermeture du driver...")
        scraper.close()
        print("✅ Driver fermé")

if __name__ == "__main__":
    url = "https://eden-daoc.net/items?m=market"
    test_scrape_url(url)
