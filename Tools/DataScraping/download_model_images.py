"""
Download and Convert Item Model Images
Downloads all item model images from Eve-of-Darkness GitHub repository
and converts them to WebP format for optimal size/quality ratio.

Source: https://github.com/Eve-of-Darkness/DolModels/tree/master/src/items
Target: Img/Models/items/

Features:
- Downloads 1000+ model images from GitHub
- Converts JPG to WebP (80% quality = ~50% size reduction)
- Progress tracking with statistics
- Resume capability (skips existing files)
- Error handling and retry logic
- Final report with size comparison

Usage:
    python Tools/DataScraping/download_model_images.py [--force] [--quality 80]
    
Arguments:
    --force     : Re-download and overwrite existing files
    --quality   : WebP quality (1-100, default: 80)
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
GITHUB_API_URL = "https://api.github.com/repos/Eve-of-Darkness/DolModels/contents/src/items"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Eve-of-Darkness/DolModels/master/src/items"
TARGET_DIR = Path(__file__).parent.parent.parent / "Img" / "Models" / "items"
DEFAULT_QUALITY = 80
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


class ModelImageDownloader:
    """Downloads and converts item model images from GitHub"""
    
    def __init__(self, force=False, quality=DEFAULT_QUALITY):
        """
        Initialize downloader
        
        Args:
            force: If True, re-download existing files
            quality: WebP compression quality (1-100)
        """
        self.force = force
        self.quality = quality
        self.target_dir = TARGET_DIR
        self.stats = {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'original_size': 0,
            'converted_size': 0
        }
        
    def get_file_list(self):
        """
        Get list of image files from GitHub API
        
        Returns:
            List of tuples: (filename, download_url, size)
        """
        try:
            logging.info(f"Fetching file list from GitHub API...")
            response = requests.get(GITHUB_API_URL, timeout=10)
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
    
    def process_file(self, filename, download_url, original_size):
        """
        Download and convert a single file
        
        Args:
            filename: Original filename (e.g., "123.jpg")
            download_url: GitHub download URL
            original_size: Original file size in bytes
            
        Returns:
            True if successful, False otherwise
        """
        # Generate output filename (change extension to .webp)
        model_id = filename.replace('.jpg', '')
        output_path = self.target_dir / f"{model_id}.webp"
        
        # Skip if already exists and not forcing
        if output_path.exists() and not self.force:
            logging.debug(f"Skipping {model_id} (already exists)")
            self.stats['skipped'] += 1
            self.stats['converted_size'] += output_path.stat().st_size
            return True
        
        # Download JPG
        logging.info(f"Downloading model {model_id}...")
        jpg_bytes = self.download_image(download_url)
        
        if not jpg_bytes:
            self.stats['failed'] += 1
            return False
        
        # Convert to WebP
        logging.info(f"Converting {model_id} to WebP (quality={self.quality})...")
        success = self.convert_to_webp(jpg_bytes, output_path)
        
        if success:
            self.stats['downloaded'] += 1
            self.stats['original_size'] += original_size
            self.stats['converted_size'] += output_path.stat().st_size
            
            logging.info(f"✅ {model_id}: {original_size/1024:.1f} KB → {output_path.stat().st_size/1024:.1f} KB")
            return True
        else:
            self.stats['failed'] += 1
            return False
    
    def run(self):
        """Execute the download and conversion process"""
        logging.info("=" * 60)
        logging.info("Item Model Images Downloader & Converter")
        logging.info("=" * 60)
        
        # Create target directory
        self.target_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Target directory: {self.target_dir}")
        
        # Get file list from GitHub
        files = self.get_file_list()
        
        if not files:
            logging.error("No files to download. Exiting.")
            return
        
        self.stats['total'] = len(files)
        
        logging.info(f"Starting download of {self.stats['total']} files...")
        logging.info(f"WebP quality: {self.quality}%")
        logging.info(f"Force re-download: {self.force}")
        logging.info("-" * 60)
        
        # Process each file
        for idx, (filename, download_url, original_size) in enumerate(files, 1):
            logging.info(f"[{idx}/{self.stats['total']}] Processing {filename}...")
            self.process_file(filename, download_url, original_size)
            
            # Small delay to avoid rate limiting
            if idx % 50 == 0:
                logging.info("Pausing 2 seconds to avoid rate limiting...")
                time.sleep(2)
        
        # Print final report
        self.print_report()
    
    def print_report(self):
        """Print final statistics report"""
        logging.info("=" * 60)
        logging.info("DOWNLOAD COMPLETED")
        logging.info("=" * 60)
        
        logging.info(f"Total files:       {self.stats['total']}")
        logging.info(f"Downloaded:        {self.stats['downloaded']}")
        logging.info(f"Skipped:           {self.stats['skipped']}")
        logging.info(f"Failed:            {self.stats['failed']}")
        
        logging.info("-" * 60)
        
        original_mb = self.stats['original_size'] / 1024 / 1024
        converted_mb = self.stats['converted_size'] / 1024 / 1024
        reduction = ((self.stats['original_size'] - self.stats['converted_size']) / 
                    self.stats['original_size'] * 100) if self.stats['original_size'] > 0 else 0
        
        logging.info(f"Original size:     {original_mb:.2f} MB")
        logging.info(f"Converted size:    {converted_mb:.2f} MB")
        logging.info(f"Size reduction:    {reduction:.1f}%")
        
        logging.info("=" * 60)
        
        if self.stats['failed'] > 0:
            logging.warning(f"⚠️ {self.stats['failed']} files failed to download/convert")
        else:
            logging.info("✅ All files processed successfully!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Download and convert DAOC item model images from GitHub"
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
    
    args = parser.parse_args()
    
    # Run downloader
    downloader = ModelImageDownloader(
        force=args.force,
        quality=args.quality
    )
    downloader.run()


if __name__ == "__main__":
    main()
