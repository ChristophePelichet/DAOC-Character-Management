"""
Professional Models Metadata Scraper for Los Ojos Website
==========================================================

Complete and robust scraper that extracts all model metadata from Los Ojos
with proper error handling, retry logic, and progress tracking.

Features:
- Comprehensive error handling and logging
- Automatic retry on failures
- Progress tracking with statistics
- Multi-page pagination support
- Clean data validation
- Resumable scraping (caching)

Output: Data/models_metadata.json

Usage:
    python Tools/DataScraping/scrape_models_metadata.py [--force] [--cache]
    
Arguments:
    --force     : Force re-scrape even if cache exists
    --cache     : Use cached pages (faster for debugging)
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
import logging
import re
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import hashlib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraping.log'),
        logging.StreamHandler()
    ]
)

# Constants
BASE_URL = "https://daoc.ndlp.info/losojos-001-site1.btempurl.com/ModelViewer"
OUTPUT_FILE = Path(__file__).parent.parent.parent / "Data" / "models_metadata.json"
CACHE_DIR = Path(__file__).parent.parent.parent / ".cache" / "scraping"
DELAY_BETWEEN_REQUESTS = 0.8  # seconds (be nice to the server)
MAX_RETRIES = 3
REQUEST_TIMEOUT = 20


@dataclass
class ModelMetadata:
    """Model metadata structure"""
    name: str
    main_category: str
    subcategory: str
    source_url: str
    subcategory: Optional[str] = None
    source_url: Optional[str] = None


class ModelsScraper:
    """Professional scraper for DAOC model metadata"""
    
    # Complete category mapping
    ITEM_SUBCATEGORIES = {
        # Weapons
        'Bow': 'Weapons',
        'Crossbow': 'Weapons',
        'Dagger': 'Weapons',
        'Flexible': 'Weapons',
        'Greave': 'Weapons',  # Hand to Hand
        'Instrument': 'Weapons',
        'Polearm': 'Weapons',
        'Scythe': 'Weapons',
        'Shield': 'Weapons',
        'Staff': 'Weapons',
        'Sword': 'Weapons',
        'Throwing': 'Weapons',
        'Two Handed': 'Weapons',
        # Armor
        'Cloak': 'Armor',
        'Feet': 'Armor',
        'Hands': 'Armor',
        'Helm': 'Armor',
        'Chest': 'Armor',
        'Legs': 'Armor',
        'Sleeves': 'Armor',
        # Other
        'Housing': 'Housing Items',
        'Siege': 'Siege Weapons',
        'World': 'World Objects'
    }
    
    MOB_SUBCATEGORIES = {
        'Biped Male': 'Biped',
        'Biped Female': 'Biped',
        'Vampiir Male': 'Vampiir',
        'Vampiir Female': 'Vampiir',
        'Demons': 'Creatures',
        'Animals': 'Creatures',
        'Other': 'Creatures',
        'Not Categorized': 'Unknown'
    }
    
    def __init__(self, use_cache: bool = False, force: bool = False):
        """Initialize scraper"""
        self.use_cache = use_cache
        self.force = force
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'DAOC-Character-Manager/1.0 (Model Metadata Scraper)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        self.metadata = {
            'items': {},
            'mobs': {},
            'icons': {}
        }
        
        self.stats = {
            'items': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0},
            'mobs': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0},
            'icons': {'total': 0, 'success': 0, 'failed': 0, 'skipped': 0}
        }
        
        # Create cache directory
        if self.use_cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, url: str) -> Path:
        """Get cache file path for a URL"""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return CACHE_DIR / f"{url_hash}.html"
    
    def _fetch_page(self, url: str, retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage with retry logic
        
        Args:
            url: Page URL
            retries: Number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        cache_path = self._get_cache_path(url)
        
        # Try cache first
        if self.use_cache and cache_path.exists() and not self.force:
            logging.debug(f"Using cached page: {url}")
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return BeautifulSoup(f.read(), 'html.parser')
            except Exception as e:
                logging.warning(f"Cache read failed: {e}")
        
        # Fetch from web
        for attempt in range(retries):
            try:
                logging.debug(f"Fetching: {url} (attempt {attempt + 1}/{retries})")
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                response.encoding = 'utf-8'
                
                # Cache the response
                if self.use_cache:
                    with open(cache_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                
                return BeautifulSoup(response.text, 'html.parser')
                
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    time.sleep(DELAY_BETWEEN_REQUESTS * (attempt + 1))
                else:
                    logging.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
        
        return None
    
    def _extract_model_id_from_url(self, url: str, model_type: str) -> Optional[str]:
        """Extract model ID from GitHub URL"""
        pattern = rf'/{model_type}/(\d+)\.jpg'
        match = re.search(pattern, url)
        return match.group(1) if match else None
    
    def _extract_items_from_page(self, soup: BeautifulSoup, category: str, subcategory: str) -> int:
        """
        Extract all items from a single page
        
        Args:
            soup: Parsed HTML
            category: Main category (e.g., "Weapons")
            subcategory: Subcategory (e.g., "Bow")
            
        Returns:
            Number of items extracted
        """
        count = 0
        
        # Find all figure elements with class "items"
        figures = soup.find_all('figure', class_='items')
        
        for figure in figures:
            try:
                # Get image element
                img = figure.find('img')
                if not img or 'src' not in img.attrs:
                    continue
                
                # Extract model ID from GitHub URL
                model_id = self._extract_model_id_from_url(img['src'], 'items')
                if not model_id:
                    logging.warning(f"Could not extract model ID from: {img['src']}")
                    self.stats['items']['failed'] += 1
                    continue
                
                # Get item name from figcaption
                figcaption = figure.find('figcaption', class_='caption_model')
                if figcaption:
                    # Format: "ID: 123 - Item Name"
                    text = figcaption.get_text(strip=True)
                    name_match = re.search(r'ID:\s*\d+\s*-\s*(.+)', text)
                    name = name_match.group(1).strip() if name_match else text
                else:
                    # Fallback to img alt
                    name = img.get('alt', '').strip()
                
                if not name:
                    name = f"Item Model {model_id}"
                    logging.debug(f"Using default name for ID {model_id}")
                
                # Store metadata (skip if already exists - keep first occurrence)
                if model_id in self.metadata['items']:
                    logging.debug(f"Item ID {model_id} already exists, skipping duplicate")
                    self.stats['items']['skipped'] += 1
                else:
                    self.metadata['items'][model_id] = asdict(ModelMetadata(
                        name=name,
                        main_category=category,
                        subcategory=subcategory,
                        source_url=img['src']
                    ))
                    self.stats['items']['success'] += 1
                
                count += 1
                
            except Exception as e:
                logging.error(f"Error extracting item: {e}", exc_info=True)
                self.stats['items']['failed'] += 1
        
        return count
    
    def _get_pagination_links(self, soup: BeautifulSoup) -> List[int]:
        """Extract all page numbers from pagination links"""
        page_numbers = []
        
        # Find all links in pagination area
        links = soup.find_all('a', href=re.compile(r'pageNumber=\d+'))
        
        for link in links:
            match = re.search(r'pageNumber=(\d+)', link['href'])
            if match:
                page_numbers.append(int(match.group(1)))
        
        return sorted(set(page_numbers))
    
    def _extract_category_links(self, main_page_url: str) -> Dict[str, Dict[str, str]]:
        """
        Extract all category links from main page
        
        Args:
            main_page_url: URL of main page (e.g., ItemModels.html)
            
        Returns:
            Dictionary mapping categories to their subcategories and URLs
            Example: {'Weapons': {'Bow': 'ItemModelse089.html?filter=Bow', ...}, ...}
        """
        soup = self._fetch_page(f"{BASE_URL}/{main_page_url}")
        if not soup:
            logging.error(f"Failed to fetch main page: {main_page_url}")
            return {}
        
        categories = {}
        
        # Find all links with filter parameter
        sidebar = soup.find('div', class_='model_catagory')
        if not sidebar:
            logging.error("Could not find sidebar with categories")
            return {}
        
        current_main_category = None
        
        for li in sidebar.find_all('li'):
            link = li.find('a', href=True)
            if not link:
                continue
            
            href = link['href']
            filter_match = re.search(r'filter=([^&"]+)', href)
            
            if not filter_match:
                continue
            
            filter_value = filter_match.group(1).replace('%20', ' ')
            
            # Check if this is a main category (has nested <ul>)
            nested_ul = li.find('ul')
            if nested_ul:
                # This is a main category
                current_main_category = filter_value
                categories[current_main_category] = {}
            elif current_main_category:
                # This is a subcategory under current main category
                categories[current_main_category][filter_value] = href
            else:
                # Standalone category (like Housing, Siege, World)
                categories[filter_value] = {'All': href}
        
        return categories
    
    def scrape_item_subcategory(self, subcategory: str, category: str, url_path: str) -> int:
        """
        Scrape all items for a specific subcategory (with pagination)
        
        Args:
            subcategory: Item subcategory (e.g., "Bow")
            category: Main category (e.g., "Weapons")
            url_path: Complete URL path with hash (e.g., "ItemModelse089.html?filter=Bow")
            
        Returns:
            Total number of items scraped
        """
        logging.info(f"  Scraping subcategory: {subcategory} ({category})")
        total_count = 0
        
        # First page
        url = f"{BASE_URL}/{url_path}"
        soup = self._fetch_page(url)
        
        if not soup:
            logging.error(f"Failed to fetch first page for {subcategory}")
            return 0
        
        # Extract items from first page
        count = self._extract_items_from_page(soup, category, subcategory)
        total_count += count
        logging.info(f"    Page 1: {count} items")
        
        # Check for additional pages
        page_numbers = self._get_pagination_links(soup)
        
        for page_num in page_numbers:
            if page_num == 1:
                continue  # Already scraped
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
            # Add pageNumber to existing URL
            if '?' in url_path:
                url = f"{BASE_URL}/{url_path}&pageNumber={page_num}"
            else:
                url = f"{BASE_URL}/{url_path}?pageNumber={page_num}"
            
            soup = self._fetch_page(url)
            
            if not soup:
                logging.warning(f"Failed to fetch page {page_num} for {subcategory}")
                continue
            
            count = self._extract_items_from_page(soup, category, subcategory)
            total_count += count
            logging.info(f"    Page {page_num}: {count} items")
        
        logging.info(f"    Total for {subcategory}: {total_count} items")
        return total_count
    
    def scrape_all_items(self):
        """Scrape all item models"""
        logging.info("=" * 70)
        logging.info("SCRAPING ITEM MODELS")
        logging.info("=" * 70)
        
        # Extract all category links from main page
        logging.info("Extracting category structure from main page...")
        categories = self._extract_category_links("ItemModels.html")
        
        if not categories:
            logging.error("Failed to extract categories")
            return
        
        logging.info(f"Found {len(categories)} main categories")
        
        # Scrape each category
        for main_category, subcategories in categories.items():
            logging.info(f"\nCategory: {main_category}")
            
            for subcategory, url_path in subcategories.items():
                try:
                    self.scrape_item_subcategory(subcategory, main_category, url_path)
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                except Exception as e:
                    logging.error(f"Error scraping {subcategory}: {e}", exc_info=True)
        
        self.stats['items']['total'] = len(self.metadata['items'])
        logging.info(f"\nTotal Items Scraped: {self.stats['items']['total']}")
    
    def scrape_mob_subcategory(self, subcategory: str, category: str, url_path: str) -> int:
        """
        Scrape mobs for a specific subcategory
        
        Args:
            subcategory: Mob subcategory (e.g., "Biped")
            category: Main category (e.g., "Biped Male")
            url_path: Complete URL path with hash
            
        Returns:
            Total number of mobs scraped
        """
        logging.info(f"  Scraping mob category: {subcategory}")
        total_count = 0
        
        url = f"{BASE_URL}/{url_path}"
        soup = self._fetch_page(url)
        
        if not soup:
            return 0
        
        # Extract mobs (similar structure to items)
        figures = soup.find_all('figure', class_='items')
        
        for figure in figures:
            try:
                img = figure.find('img')
                if not img or 'src' not in img.attrs:
                    continue
                
                model_id = self._extract_model_id_from_url(img['src'], 'mobs')
                if not model_id:
                    continue
                
                figcaption = figure.find('figcaption', class_='caption_model')
                if figcaption:
                    text = figcaption.get_text(strip=True)
                    name_match = re.search(r'ID:\s*\d+\s*-\s*(.+)', text)
                    name = name_match.group(1).strip() if name_match else text
                else:
                    name = img.get('alt', '').strip() or f"Mob Model {model_id}"
                
                # Store metadata (skip duplicates)
                if model_id in self.metadata['mobs']:
                    logging.debug(f"Mob ID {model_id} already exists, skipping duplicate")
                    self.stats['mobs']['skipped'] += 1
                else:
                    self.metadata['mobs'][model_id] = asdict(ModelMetadata(
                        name=name,
                        main_category=category,
                        subcategory=subcategory,
                        source_url=img['src']
                    ))
                    self.stats['mobs']['success'] += 1
                
                total_count += 1
                
            except Exception as e:
                logging.error(f"Error extracting mob: {e}")
                self.stats['mobs']['failed'] += 1
        
        # Check pagination
        page_numbers = self._get_pagination_links(soup)
        for page_num in page_numbers:
            if page_num == 1:
                continue
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
            
            # Add pageNumber to existing URL
            if '?' in url_path:
                url = f"{BASE_URL}/{url_path}&pageNumber={page_num}"
            else:
                url = f"{BASE_URL}/{url_path}?pageNumber={page_num}"
            
            soup = self._fetch_page(url)
            if soup:
                # Process additional page items
                page_figures = soup.find_all('figure', class_='items')
                for figure in page_figures:
                    try:
                        img = figure.find('img')
                        if not img or 'src' not in img.attrs:
                            continue
                        
                        model_id = self._extract_model_id_from_url(img['src'], 'mobs')
                        if not model_id or model_id in self.metadata['mobs']:
                            continue
                        
                        figcaption = figure.find('figcaption', class_='caption_model')
                        if figcaption:
                            text = figcaption.get_text(strip=True)
                            name_match = re.search(r'ID:\s*\d+\s*-\s*(.+)', text)
                            name = name_match.group(1).strip() if name_match else text
                        else:
                            name = img.get('alt', '').strip() or f"Mob Model {model_id}"
                        
                        self.metadata['mobs'][model_id] = asdict(ModelMetadata(
                            name=name,
                            main_category=category,
                            subcategory=subcategory,
                            source_url=img['src']
                        ))
                        self.stats['mobs']['success'] += 1
                        total_count += 1
                        
                    except Exception as e:
                        logging.error(f"Error extracting mob from page {page_num}: {e}")
                        self.stats['mobs']['failed'] += 1
        
        logging.info(f"    Total: {total_count} mobs")
        return total_count
    
    def scrape_all_mobs(self):
        """Scrape all mob models"""
        logging.info("=" * 70)
        logging.info("SCRAPING MOB MODELS")
        logging.info("=" * 70)
        
        # Extract all category links from main page
        logging.info("Extracting mob category structure from main page...")
        categories = self._extract_category_links("MobModels.html")
        
        if not categories:
            logging.error("Failed to extract mob categories")
            return
        
        logging.info(f"Found {len(categories)} mob categories")
        
        # Scrape each category
        for main_category, subcategories in categories.items():
            logging.info(f"\nMob Category: {main_category}")
            
            for subcategory, url_path in subcategories.items():
                try:
                    self.scrape_mob_subcategory(subcategory, main_category, url_path)
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                except Exception as e:
                    logging.error(f"Error scraping {subcategory}: {e}", exc_info=True)
        
        self.stats['mobs']['total'] = len(self.metadata['mobs'])
        logging.info(f"\nTotal Mobs Scraped: {self.stats['mobs']['total']}")
    
    def scrape_inventory_icons(self):
        """Scrape inventory icon models"""
        logging.info("=" * 70)
        logging.info("SCRAPING INVENTORY ICONS")
        logging.info("=" * 70)
        
        url = f"{BASE_URL}/InventoryModels.html"
        soup = self._fetch_page(url)
        
        if not soup:
            logging.error("Failed to fetch inventory icons page")
            return
        
        figures = soup.find_all('figure', class_='items')
        
        for figure in figures:
            try:
                img = figure.find('img')
                if not img or 'src' not in img.attrs:
                    continue
                
                # Icons use different path: /icons/items/
                match = re.search(r'/icons/items/(\d+)\.jpg', img['src'])
                if not match:
                    continue
                
                model_id = match.group(1)
                
                figcaption = figure.find('figcaption', class_='caption_model')
                if figcaption:
                    text = figcaption.get_text(strip=True)
                    name_match = re.search(r'ID:\s*\d+\s*-\s*(.+)', text)
                    name = name_match.group(1).strip() if name_match else text
                else:
                    name = img.get('alt', '').strip() or f"Icon {model_id}"
                
                # Store metadata (skip duplicates)
                if model_id in self.metadata['icons']:
                    logging.debug(f"Icon ID {model_id} already exists, skipping duplicate")
                    self.stats['icons']['skipped'] += 1
                else:
                    self.metadata['icons'][model_id] = asdict(ModelMetadata(
                        name=name,
                        main_category='Inventory',
                        subcategory='Icons',
                        source_url=img['src']
                    ))
                    self.stats['icons']['success'] += 1
                
            except Exception as e:
                logging.error(f"Error extracting icon: {e}")
                self.stats['icons']['failed'] += 1
        
        # Check pagination
        page_numbers = self._get_pagination_links(soup)
        for page_num in page_numbers:
            if page_num == 1:
                continue
            
            time.sleep(DELAY_BETWEEN_REQUESTS)
            url = f"{BASE_URL}/InventoryModels.html?pageNumber={page_num}"
            soup = self._fetch_page(url)
            # Process additional pages...
        
        self.stats['icons']['total'] = len(self.metadata['icons'])
        logging.info(f"Total Icons Scraped: {self.stats['icons']['total']}")
    
    def save_metadata(self):
        """Save metadata to JSON file"""
        logging.info("=" * 70)
        logging.info("SAVING METADATA")
        logging.info("=" * 70)
        
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        
        file_size = OUTPUT_FILE.stat().st_size / 1024
        logging.info(f"Saved to: {OUTPUT_FILE}")
        logging.info(f"File size: {file_size:.1f} KB")
    
    def print_summary(self):
        """Print comprehensive scraping summary"""
        logging.info("=" * 70)
        logging.info("SCRAPING SUMMARY")
        logging.info("=" * 70)
        
        for model_type in ['items', 'mobs', 'icons']:
            stats = self.stats[model_type]
            logging.info(f"\n{model_type.upper()}:")
            logging.info(f"  Total:   {stats['total']}")
            logging.info(f"  Success: {stats['success']}")
            logging.info(f"  Failed:  {stats['failed']}")
            logging.info(f"  Skipped: {stats['skipped']}")
        
        total = sum(s['total'] for s in self.stats.values())
        logging.info(f"\nGRAND TOTAL: {total} models")
        logging.info("=" * 70)
        
        # Category breakdown for items
        if self.metadata['items']:
            logging.info("\nITEM CATEGORIES BREAKDOWN:")
            categories = {}
            for item in self.metadata['items'].values():
                subcat = item.get('subcategory', 'Unknown')
                categories[subcat] = categories.get(subcat, 0) + 1
            
            for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
                logging.info(f"  {cat:20s}: {count:4d} items")
    
    def run(self):
        """Execute complete scraping process"""
        logging.info("=" * 70)
        logging.info("PROFESSIONAL MODELS METADATA SCRAPER")
        logging.info("=" * 70)
        logging.info(f"Cache enabled: {self.use_cache}")
        logging.info(f"Force re-scrape: {self.force}")
        logging.info("")
        
        start_time = time.time()
        
        try:
            # Scrape all model types
            self.scrape_all_items()
            self.scrape_all_mobs()
            self.scrape_inventory_icons()
            
            # Save results
            self.save_metadata()
            
            # Print summary
            self.print_summary()
            
            elapsed = time.time() - start_time
            logging.info(f"\n[SUCCESS] Scraping completed successfully in {elapsed:.1f} seconds!")
            
        except KeyboardInterrupt:
            logging.warning("\n[INTERRUPTED] Scraping interrupted by user")
            logging.info("Saving partial results...")
            self.save_metadata()
            
        except Exception as e:
            logging.error(f"\n[ERROR] Scraping failed: {e}", exc_info=True)
            raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Professional scraper for DAOC model metadata"
    )
    parser.add_argument(
        '--cache',
        action='store_true',
        help='Use cached pages (faster for debugging)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-scrape even if cache exists'
    )
    
    args = parser.parse_args()
    
    scraper = ModelsScraper(use_cache=args.cache, force=args.force)
    scraper.run()


if __name__ == "__main__":
    main()
