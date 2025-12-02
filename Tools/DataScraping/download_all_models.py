"""
Download and Convert ALL Model Images (Items, Mobs, Inventory Icons)
Downloads all model images from Eve-of-Darkness GitHub repository
and converts them to WebP format for optimal size/quality ratio.

Sources:
- Items:     https://github.com/Eve-of-Darkness/DolModels/tree/master/src/items
- Mobs:      https://github.com/Eve-of-Darkness/DolModels/tree/master/src/mobs
- Icons:     https://github.com/Eve-of-Darkness/DolModels/tree/master/src/icons/items

Targets:
- Items:     Img/Models/items/
- Mobs:      Img/Models/mobs/
- Icons:     Img/Models/icons/items/

Features:
- Downloads all 3 model types (Items, Mobs, Inventory Icons)
- Converts JPG to WebP (80% quality = ~50% size reduction)
- Progress tracking with statistics per type
- Resume capability (skips existing files)
- Error handling and retry logic
- Final report with size comparison

Usage:
    python Tools/DataScraping/download_all_models.py [--force] [--quality 80] [--type all]
    
Arguments:
    --force     : Re-download and overwrite existing files
    --quality   : WebP quality (1-100, default: 80)
    --type      : Model type to download: items, mobs, icons, all (default: all)
"""
import requests
import time
from pathlib import Path
from PIL import Image
from io import BytesIO
import argparse
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants
GITHUB_API_BASE = "https://api.github.com/repos/Eve-of-Darkness/DolModels/contents/src"
GITHUB_RAW_BASE = "https://raw.githubusercontent.com/Eve-of-Darkness/DolModels/master/src"

# Model types configuration
MODEL_TYPES = {
    'items': {
        'api_path': f"{GITHUB_API_BASE}/items",
        'raw_path': f"{GITHUB_RAW_BASE}/items",
        'target_dir': Path(__file__).parent.parent.parent / "Img" / "Models" / "items"
    },
    'mobs': {
        'api_path': f"{GITHUB_API_BASE}/mobs",
        'raw_path': f"{GITHUB_RAW_BASE}/mobs",
        'target_dir': Path(__file__).parent.parent.parent / "Img" / "Models" / "mobs"
    },
    'icons': {
        'api_path': f"{GITHUB_API_BASE}/icons/items",
        'raw_path': f"{GITHUB_RAW_BASE}/icons/items",
        'target_dir': Path(__file__).parent.parent.parent / "Img" / "Models" / "icons" / "items"
    }
}

DEFAULT_QUALITY = 80
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class AllModelsDownloader:
    """Downloads and converts all model types from GitHub"""
    
    def __init__(self, force=False, quality=DEFAULT_QUALITY, model_type='all'):
        """
        Initialize downloader
        
        Args:
            force: If True, re-download existing files
            quality: WebP compression quality (1-100)
            model_type: Type to download (items, mobs, icons, all)
        """
        self.force = force
        self.quality = quality
        self.model_type = model_type
        
        # Global statistics
        self.global_stats = {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'original_size': 0,
            'converted_size': 0
        }
        
        # Per-type statistics
        self.type_stats = {
            'items': self._new_stats(),
            'mobs': self._new_stats(),
            'icons': self._new_stats()
        }
        
    def _new_stats(self):
        """Create new statistics dict"""
        return {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'original_size': 0,
            'converted_size': 0
        }
    
    def get_file_list(self, api_url):
        """
        Get list of image files from GitHub API
        
        Args:
            api_url: GitHub API URL for directory
            
        Returns:
            List of tuples: (filename, download_url, size)
        """
        try:
            logging.info(f"Fetching file list from GitHub API...")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Filter JPG files only
            files = [
                (item['name'], item['download_url'], item['size'])
                for item in data
                if item['name'].endswith('.jpg')
            ]
            
            logging.info(f"Found {len(files)} JPG files")
            return files
            
        except Exception as e:
            logging.error(f"Failed to fetch file list: {e}")
            return []
    
    def download_image(self, url, retries=MAX_RETRIES):
        """
        Download image from URL with retry logic
        
        Args:
            url: Image URL
            retries: Number of retry attempts
            
        Returns:
            Image bytes or None if failed
        """
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                return response.content
            except Exception as e:
                if attempt < retries - 1:
                    logging.warning(f"Download attempt {attempt + 1} failed, retrying... ({e})")
                    time.sleep(RETRY_DELAY)
                else:
                    logging.error(f"Failed to download after {retries} attempts: {e}")
                    return None
    
    def convert_to_webp(self, jpg_bytes, output_path):
        """
        Convert JPG bytes to WebP format
        
        Args:
            jpg_bytes: Original JPG image bytes
            output_path: Path to save WebP file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open JPG from bytes
            img = Image.open(BytesIO(jpg_bytes))
            
            # Convert to RGB if needed (WebP doesn't support some modes)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as WebP
            img.save(
                output_path,
                'WEBP',
                quality=self.quality,
                method=6  # Best compression (slower but smaller)
            )
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to convert image: {e}")
            return False
    
    def process_file(self, filename, download_url, original_size, target_dir, stats):
        """
        Download and convert a single file
        
        Args:
            filename: Original filename (e.g., "123.jpg")
            download_url: GitHub download URL
            original_size: Original file size in bytes
            target_dir: Target directory for output
            stats: Statistics dict to update
            
        Returns:
            True if successful, False otherwise
        """
        # Generate output filename (change extension to .webp)
        model_id = filename.replace('.jpg', '')
        output_path = target_dir / f"{model_id}.webp"
        
        # Skip if already exists and not forcing
        if output_path.exists() and not self.force:
            logging.debug(f"Skipping {model_id} (already exists)")
            stats['skipped'] += 1
            stats['converted_size'] += output_path.stat().st_size
            return True
        
        # Download JPG
        logging.info(f"Downloading model {model_id}...")
        jpg_bytes = self.download_image(download_url)
        
        if not jpg_bytes:
            stats['failed'] += 1
            return False
        
        # Convert to WebP
        logging.info(f"Converting {model_id} to WebP (quality={self.quality})...")
        success = self.convert_to_webp(jpg_bytes, output_path)
        
        if success:
            stats['downloaded'] += 1
            stats['original_size'] += original_size
            stats['converted_size'] += output_path.stat().st_size
            
            logging.info(f"✅ {model_id}: {original_size/1024:.1f} KB → {output_path.stat().st_size/1024:.1f} KB")
            return True
        else:
            stats['failed'] += 1
            return False
    
    def download_type(self, type_name):
        """
        Download all models for a specific type
        
        Args:
            type_name: Type name (items, mobs, icons)
        """
        logging.info("=" * 60)
        logging.info(f"Downloading {type_name.upper()} Models")
        logging.info("=" * 60)
        
        config = MODEL_TYPES[type_name]
        stats = self.type_stats[type_name]
        
        # Create target directory
        config['target_dir'].mkdir(parents=True, exist_ok=True)
        logging.info(f"Target directory: {config['target_dir']}")
        
        # Get file list from GitHub
        files = self.get_file_list(config['api_path'])
        
        if not files:
            logging.error(f"No files to download for {type_name}. Skipping.")
            return
        
        stats['total'] = len(files)
        
        logging.info(f"Starting download of {stats['total']} files...")
        logging.info(f"WebP quality: {self.quality}%")
        logging.info(f"Force re-download: {self.force}")
        logging.info("-" * 60)
        
        # Process each file
        for idx, (filename, download_url, original_size) in enumerate(files, 1):
            logging.info(f"[{idx}/{stats['total']}] Processing {filename}...")
            self.process_file(filename, download_url, original_size, config['target_dir'], stats)
            
            # Small delay to avoid rate limiting
            if idx % 50 == 0:
                logging.info("Pausing 2 seconds to avoid rate limiting...")
                time.sleep(2)
        
        # Print type summary
        self.print_type_summary(type_name)
    
    def print_type_summary(self, type_name):
        """Print summary for a specific type"""
        stats = self.type_stats[type_name]
        
        logging.info("-" * 60)
        logging.info(f"{type_name.upper()} Summary:")
        logging.info(f"  Total files:       {stats['total']}")
        logging.info(f"  Downloaded:        {stats['downloaded']}")
        logging.info(f"  Skipped:           {stats['skipped']}")
        logging.info(f"  Failed:            {stats['failed']}")
        
        if stats['original_size'] > 0:
            original_mb = stats['original_size'] / 1024 / 1024
            converted_mb = stats['converted_size'] / 1024 / 1024
            reduction = ((stats['original_size'] - stats['converted_size']) / 
                        stats['original_size'] * 100)
            
            logging.info(f"  Original size:     {original_mb:.2f} MB")
            logging.info(f"  Converted size:    {converted_mb:.2f} MB")
            logging.info(f"  Size reduction:    {reduction:.1f}%")
    
    def calculate_global_stats(self):
        """Calculate global statistics from all types"""
        for stats in self.type_stats.values():
            self.global_stats['total'] += stats['total']
            self.global_stats['downloaded'] += stats['downloaded']
            self.global_stats['skipped'] += stats['skipped']
            self.global_stats['failed'] += stats['failed']
            self.global_stats['original_size'] += stats['original_size']
            self.global_stats['converted_size'] += stats['converted_size']
    
    def print_global_report(self):
        """Print final global statistics report"""
        self.calculate_global_stats()
        
        logging.info("=" * 60)
        logging.info("GLOBAL DOWNLOAD REPORT")
        logging.info("=" * 60)
        
        logging.info(f"Total files:       {self.global_stats['total']}")
        logging.info(f"Downloaded:        {self.global_stats['downloaded']}")
        logging.info(f"Skipped:           {self.global_stats['skipped']}")
        logging.info(f"Failed:            {self.global_stats['failed']}")
        
        logging.info("-" * 60)
        
        if self.global_stats['original_size'] > 0:
            original_mb = self.global_stats['original_size'] / 1024 / 1024
            converted_mb = self.global_stats['converted_size'] / 1024 / 1024
            reduction = ((self.global_stats['original_size'] - self.global_stats['converted_size']) / 
                        self.global_stats['original_size'] * 100)
            
            logging.info(f"Original size:     {original_mb:.2f} MB")
            logging.info(f"Converted size:    {converted_mb:.2f} MB")
            logging.info(f"Size reduction:    {reduction:.1f}%")
        
        logging.info("=" * 60)
        
        # Per-type breakdown
        logging.info("Per-Type Breakdown:")
        for type_name in ['items', 'mobs', 'icons']:
            stats = self.type_stats[type_name]
            if stats['total'] > 0:
                converted_mb = stats['converted_size'] / 1024 / 1024
                logging.info(f"  {type_name.capitalize():8s}: {stats['total']:4d} files, {converted_mb:6.2f} MB")
        
        logging.info("=" * 60)
        
        if self.global_stats['failed'] > 0:
            logging.warning(f"⚠️ {self.global_stats['failed']} files failed to download/convert")
        else:
            logging.info("✅ All files processed successfully!")
    
    def run(self):
        """Execute the download and conversion process"""
        logging.info("=" * 60)
        logging.info("ALL Models Downloader & Converter")
        logging.info("=" * 60)
        
        # Determine which types to download
        if self.model_type == 'all':
            types_to_download = ['items', 'mobs', 'icons']
        else:
            types_to_download = [self.model_type]
        
        logging.info(f"Model types to download: {', '.join(types_to_download)}")
        logging.info("")
        
        # Download each type
        for type_name in types_to_download:
            self.download_type(type_name)
        
        # Print global report
        self.print_global_report()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download and convert ALL DAOC model images from GitHub (Items, Mobs, Icons)"
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Re-download and overwrite existing files'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=DEFAULT_QUALITY,
        choices=range(1, 101),
        metavar='[1-100]',
        help=f'WebP compression quality (default: {DEFAULT_QUALITY})'
    )
    parser.add_argument(
        '--type',
        type=str,
        default='all',
        choices=['items', 'mobs', 'icons', 'all'],
        help='Model type to download (default: all)'
    )
    
    args = parser.parse_args()
    
    # Run downloader
    downloader = AllModelsDownloader(
        force=args.force,
        quality=args.quality,
        model_type=args.type
    )
    downloader.run()


if __name__ == "__main__":
    main()
