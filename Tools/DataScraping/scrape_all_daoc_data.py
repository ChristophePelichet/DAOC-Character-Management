"""
DAOC Complete Data Scraper
===========================

Unified script to scrape all DAOC data from multiple sources:
1. Armor Resist Tables (darkageofcamelot.com)
2. Realm Ranks (darkageofcamelot.com)
3. Model Images from GitHub (item models 1-5000)
4. Models Metadata from Los Ojos (optional, JavaScript-rendered)

Usage:
    python Tools/DataScraping/scrape_all_daoc_data.py [options]
    
Options:
    --armor-resists     : Scrape armor resistance tables
    --realm-ranks       : Scrape realm ranks data
    --item-models       : Download all item model images (1-5000)
    --all               : Run all scrapers (default)
    --skip-existing     : Skip already downloaded models (default: True)

Examples:
    python scrape_all_daoc_data.py --all
    python scrape_all_daoc_data.py --armor-resists --realm-ranks
    python scrape_all_daoc_data.py --item-models
"""
import requests
from bs4 import BeautifulSoup
import json
import re
import urllib3
from pathlib import Path
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import argparse
import sys

# Disable SSL warnings (corporate proxy issue)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data"
MODELS_DIR = PROJECT_ROOT / "Img" / "Models" / "items"

# Create directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# ARMOR RESISTS SCRAPER
# ============================================================================

def scrape_armor_resists():
    """Scrape armor resistance tables from official DAOC website"""
    url = "https://www.darkageofcamelot.com/armor-resist-tables/"
    output_file = DATA_DIR / "armor_resists.json"
    
    logging.info("=" * 80)
    logging.info("ARMOR RESISTS SCRAPER")
    logging.info("=" * 80)
    logging.info(f"Source: {url}")
    logging.info(f"Output: {output_file}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        armor_data = {
            "armor_types": [],
            "resist_types": [],
            "tables": {}
        }
        
        tables = soup.find_all('table')
        if not tables:
            raise Exception("No tables found on page")
        
        logging.info(f"Found {len(tables)} table(s), parsing data...")
        
        for table_idx, table in enumerate(tables):
            # Find table title
            table_title = "Unknown"
            prev_element = table.find_previous(['h2', 'h3', 'h4', 'p'])
            if prev_element:
                table_title = prev_element.get_text(strip=True)
            
            rows = table.find_all('tr')
            if len(rows) < 2:
                continue
            
            # Extract headers
            headers_list = []
            header_row = rows[0]
            for cell in header_row.find_all(['th', 'td']):
                headers_list.append(cell.get_text(strip=True))
            
            # Extract data rows
            table_data = []
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if len(cells) < 2:
                    continue
                
                row_data = {}
                for idx, cell in enumerate(cells):
                    if idx < len(headers_list):
                        cell_text = cell.get_text(strip=True).replace('%', '').strip()
                        row_data[headers_list[idx]] = cell_text
                
                if row_data:
                    table_data.append(row_data)
            
            armor_data["tables"][f"table_{table_idx + 1}"] = {
                "title": table_title,
                "headers": headers_list,
                "data": table_data
            }
            
            # Collect unique armor types (first column)
            if headers_list and table_data:
                first_header = headers_list[0]
                for row in table_data:
                    armor_type = row.get(first_header, "")
                    if armor_type and armor_type not in armor_data["armor_types"]:
                        armor_data["armor_types"].append(armor_type)
            
            # Collect resist types (other columns)
            for header in headers_list[1:]:
                if header and header not in armor_data["resist_types"]:
                    armor_data["resist_types"].append(header)
            
            logging.info(f"  Table {table_idx + 1}: {table_title} - {len(table_data)} rows")
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(armor_data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"✅ Saved {len(armor_data['tables'])} tables to {output_file.name}")
        logging.info(f"   - Armor types: {len(armor_data['armor_types'])}")
        logging.info(f"   - Resist types: {len(armor_data['resist_types'])}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to scrape armor resists: {e}")
        return False


# ============================================================================
# REALM RANKS SCRAPER
# ============================================================================

def scrape_realm_ranks():
    """Scrape realm ranks data from official DAOC website"""
    url = "https://www.darkageofcamelot.com/realm-ranks/"
    
    logging.info("=" * 80)
    logging.info("REALM RANKS SCRAPER")
    logging.info("=" * 80)
    logging.info(f"Source: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        realm_data = {
            "Albion": [],
            "Hibernia": [],
            "Midgard": []
        }
        
        table = soup.find('table')
        if not table:
            raise Exception("No table found on page")
        
        rows = table.find_all('tr')
        logging.info(f"Found table with {len(rows)} rows")
        
        # Parse each data row (skip header)
        for row_idx, row in enumerate(rows[1:], 1):
            cells = row.find_all(['td', 'th'])
            if len(cells) < 5:
                continue
            
            # Cell 0: Rank and skill bonus
            rank_cell = cells[0]
            rank_text = rank_cell.get_text()
            rank_match = re.search(r'Rank (\d+)', rank_text)
            rank = int(rank_match.group(1)) if rank_match else row_idx
            
            skill_bonus_match = re.search(r'\+(\d+) to skills', rank_text)
            skill_bonus = int(skill_bonus_match.group(1)) if skill_bonus_match else 0
            
            # Cell 1: Titles (Albion, Hibernia, Midgard)
            title_cell = cells[1]
            title_lines = [line.strip() for line in title_cell.stripped_strings]
            
            albion_title = title_lines[0] if len(title_lines) > 0 else ""
            hibernia_title = title_lines[1] if len(title_lines) > 1 else ""
            midgard_title = title_lines[2] if len(title_lines) > 2 else ""
            
            # Cell 2: Levels
            level_cell = cells[2]
            levels = [line.strip() for line in level_cell.stripped_strings if line.strip()]
            
            # Cell 3: Realm Points
            rp_cell = cells[3]
            realm_points = [line.strip().replace(',', '') for line in rp_cell.stripped_strings if line.strip()]
            
            # Cell 4: Realm Ability Points
            rap_cell = cells[4]
            realm_ability_points = [line.strip() for line in rap_cell.stripped_strings if line.strip()]
            
            # Create entry for each level
            num_levels = len(levels)
            
            for i in range(num_levels):
                level = levels[i] if i < len(levels) else f"{rank}L{i+1}"
                rp = int(realm_points[i]) if i < len(realm_points) else 0
                rap = int(realm_ability_points[i]) if i < len(realm_ability_points) else 0
                
                realm_data["Albion"].append({
                    "rank": rank,
                    "skill_bonus": skill_bonus,
                    "title": albion_title,
                    "level": level,
                    "realm_points": rp,
                    "realm_ability_points": rap
                })
                
                realm_data["Hibernia"].append({
                    "rank": rank,
                    "skill_bonus": skill_bonus,
                    "title": hibernia_title,
                    "level": level,
                    "realm_points": rp,
                    "realm_ability_points": rap
                })
                
                realm_data["Midgard"].append({
                    "rank": rank,
                    "skill_bonus": skill_bonus,
                    "title": midgard_title,
                    "level": level,
                    "realm_points": rp,
                    "realm_ability_points": rap
                })
        
        # Save separate files per realm
        output_files = {
            "Albion": DATA_DIR / "realm_ranks_albion.json",
            "Hibernia": DATA_DIR / "realm_ranks_hibernia.json",
            "Midgard": DATA_DIR / "realm_ranks_midgard.json"
        }
        
        for realm, data in realm_data.items():
            with open(output_files[realm], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logging.info(f"✅ Saved {len(data)} {realm} ranks to {output_files[realm].name}")
        
        # Save combined file
        combined_file = DATA_DIR / "realm_ranks.json"
        with open(combined_file, 'w', encoding='utf-8') as f:
            json.dump(realm_data, f, indent=2, ensure_ascii=False)
        logging.info(f"✅ Saved combined realm ranks to {combined_file.name}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Failed to scrape realm ranks: {e}")
        return False


# ============================================================================
# ITEM MODELS DOWNLOADER
# ============================================================================

# Statistics
stats = {
    'total': 0,
    'already_exist': 0,
    'downloaded': 0,
    'not_found': 0,
    'failed': 0,
    'original_size': 0,
    'converted_size': 0
}

def download_and_convert_model(model_id):
    """Download and convert a single model ID from GitHub"""
    global stats
    
    output_path = MODELS_DIR / f"{model_id}.webp"
    
    # Skip if already exists
    if output_path.exists():
        stats['already_exist'] += 1
        return f"SKIP:{model_id}"
    
    # Download from GitHub
    url = f"https://raw.githubusercontent.com/Eve-of-Darkness/DolModels/master/src/items/{model_id}.jpg"
    
    try:
        response = requests.get(url, timeout=10, verify=False)
        
        if response.status_code == 404:
            stats['not_found'] += 1
            return f"404:{model_id}"
        
        response.raise_for_status()
        jpg_bytes = response.content
        original_size = len(jpg_bytes)
        
        # Convert to WebP
        img = Image.open(BytesIO(jpg_bytes))
        
        # Convert to RGB if needed
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as WebP
        img.save(output_path, 'WEBP', quality=80, method=6)
        converted_size = output_path.stat().st_size
        
        stats['downloaded'] += 1
        stats['original_size'] += original_size
        stats['converted_size'] += converted_size
        
        reduction = ((original_size - converted_size) / original_size * 100) if original_size > 0 else 0
        return f"OK:{model_id} ({original_size//1024}KB→{converted_size//1024}KB, -{reduction:.0f}%)"
        
    except Exception as e:
        stats['failed'] += 1
        return f"FAIL:{model_id} ({str(e)[:50]})"


def download_item_models(max_id=5000, max_workers=20, skip_existing=True):
    """Download all item model images from GitHub"""
    
    logging.info("=" * 80)
    logging.info("ITEM MODELS DOWNLOADER")
    logging.info("=" * 80)
    logging.info(f"Target: {MODELS_DIR}")
    logging.info(f"Range: 1 to {max_id}")
    logging.info(f"Quality: 80% WebP")
    logging.info(f"Workers: {max_workers} parallel")
    logging.info("=" * 80)
    
    # Check existing files
    existing = set()
    for f in MODELS_DIR.glob("*.webp"):
        try:
            existing.add(int(f.stem))
        except:
            pass
    
    logging.info(f"\nAlready exist: {len(existing)} files")
    
    # Prepare IDs to download
    all_ids = set(range(1, max_id + 1))
    
    if skip_existing:
        to_download = sorted(all_ids - existing)
        logging.info(f"Will download: {len(to_download)} missing IDs\n")
    else:
        to_download = sorted(all_ids)
        logging.info(f"Will test: {len(to_download)} IDs (including existing)\n")
    
    stats['total'] = len(to_download)
    
    if not to_download:
        logging.info("✅ All models already downloaded!")
        return True
    
    logging.info(f"Downloading {len(to_download)} models...")
    logging.info("=" * 80)
    
    # Download in parallel
    completed = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(download_and_convert_model, mid): mid for mid in to_download}
        
        for future in as_completed(futures):
            completed += 1
            result = future.result()
            
            # Show progress every 100 downloads
            if completed % 100 == 0:
                logging.info(f"\n[{completed}/{len(to_download)}] Progress:")
                logging.info(f"  Downloaded: {stats['downloaded']}, 404: {stats['not_found']}, Failed: {stats['failed']}")
            
            # Show successful downloads (less verbose)
            if result.startswith("OK:") and completed % 10 == 0:
                logging.debug(f"  ✅ {result[3:]}")
    
    # Final stats
    logging.info("\n" + "=" * 80)
    logging.info("DOWNLOAD COMPLETE")
    logging.info("=" * 80)
    logging.info(f"Total tested:    {stats['total']}")
    logging.info(f"Already existed: {stats['already_exist']}")
    logging.info(f"Downloaded:      {stats['downloaded']}")
    logging.info(f"Not found (404): {stats['not_found']}")
    logging.info(f"Failed:          {stats['failed']}")
    
    if stats['original_size'] > 0:
        reduction = ((stats['original_size'] - stats['converted_size']) / stats['original_size'] * 100)
        logging.info(f"\nOriginal size:   {stats['original_size'] / 1024 / 1024:.2f} MB")
        logging.info(f"Converted size:  {stats['converted_size'] / 1024 / 1024:.2f} MB")
        logging.info(f"Size reduction:  {reduction:.1f}%")
    
    # Count final total
    final_count = len(list(MODELS_DIR.glob("*.webp")))
    logging.info(f"\n✅ Total files in {MODELS_DIR.name}/: {final_count}")
    logging.info("=" * 80)
    
    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(
        description='DAOC Complete Data Scraper - Unified script for all DAOC data sources',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--armor-resists', action='store_true',
                        help='Scrape armor resistance tables')
    parser.add_argument('--realm-ranks', action='store_true',
                        help='Scrape realm ranks data')
    parser.add_argument('--item-models', action='store_true',
                        help='Download all item model images (1-5000)')
    parser.add_argument('--all', action='store_true',
                        help='Run all scrapers (default)')
    parser.add_argument('--max-id', type=int, default=5000,
                        help='Maximum model ID to download (default: 5000)')
    parser.add_argument('--workers', type=int, default=20,
                        help='Number of parallel workers for model downloads (default: 20)')
    parser.add_argument('--no-skip-existing', action='store_true',
                        help='Do not skip existing model files')
    
    args = parser.parse_args()
    
    # If no specific option, run all
    if not (args.armor_resists or args.realm_ranks or args.item_models):
        args.all = True
    
    results = {}
    
    # Run requested scrapers
    if args.all or args.armor_resists:
        logging.info("\n")
        results['armor_resists'] = scrape_armor_resists()
    
    if args.all or args.realm_ranks:
        logging.info("\n")
        results['realm_ranks'] = scrape_realm_ranks()
    
    if args.all or args.item_models:
        logging.info("\n")
        skip_existing = not args.no_skip_existing
        results['item_models'] = download_item_models(
            max_id=args.max_id,
            max_workers=args.workers,
            skip_existing=skip_existing
        )
    
    # Summary
    logging.info("\n" + "=" * 80)
    logging.info("SCRAPING SUMMARY")
    logging.info("=" * 80)
    
    for task, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logging.info(f"{task.replace('_', ' ').title()}: {status}")
    
    logging.info("=" * 80)
    
    # Exit code
    all_success = all(results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
