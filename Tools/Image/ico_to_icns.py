"""
Convert ICO image to ICNS format for macOS applications.

This utility converts Windows ICO files to macOS ICNS format by creating
the required icon sizes and packaging them into a valid ICNS file.
"""

import os
import struct
from pathlib import Path
from PIL import Image


def image_convert_ico_to_icns(input_ico: str, output_icns: str) -> bool:
    """
    Convert an ICO file to ICNS format for macOS.

    Args:
        input_ico: Path to the source .ico file
        output_icns: Path to the output .icns file

    Returns:
        True if conversion succeeded, False otherwise
    """
    try:
        # Verify input file exists
        if not os.path.exists(input_ico):
            print(f"ERROR: Input file not found: {input_ico}")
            return False

        # Open the ICO file
        img = Image.open(input_ico)
        
        # Convert RGBA if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            if img.mode == 'P':
                img = img.convert('RGBA')
        else:
            img = img.convert('RGB')

        # ICNS requires specific sizes: 16, 32, 64, 128, 256, 512, 1024
        icns_sizes = [16, 32, 64, 128, 256, 512, 1024]
        
        # Create output directory if needed
        output_dir = os.path.dirname(output_icns)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Create ICNS file with icon family header
        with open(output_icns, 'wb') as f:
            # ICNS file header
            f.write(b'icns')
            
            # Placeholder for file size (will update later)
            file_size_offset = f.tell()
            f.write(struct.pack('>I', 0))  # Temporary size
            
            icons_data = b''
            
            # Add each size
            for size in icns_sizes:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                
                if resized.mode == 'RGB':
                    resized = resized.convert('RGBA')
                
                # Get pixel data
                pixels = resized.tobytes()
                
                # Determine icon type
                if size <= 256:
                    icon_type = {
                        16: b'is32',    # 16x16 icon
                        32: b'il32',    # 32x32 icon
                        64: b'il32',    # 64x64 icon
                        128: b'it32',   # 128x128 icon
                        256: b'ic08',   # 256x256 icon
                    }.get(size, b'ic08')
                else:
                    icon_type = b'ic09'  # 512x512 icon or larger
                
                # Create icon entry
                icon_size = 8 + len(pixels)
                icons_data += icon_type
                icons_data += struct.pack('>I', icon_size)
                icons_data += pixels
            
            # Write all icon data
            f.write(icons_data)
            
            # Update file size
            total_size = 8 + len(icons_data)
            f.seek(file_size_offset)
            f.write(struct.pack('>I', total_size))
        
        print(f"✅ Successfully converted: {input_ico} -> {output_icns}")
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return False


if __name__ == '__main__':
    # Default conversion from Img/app_icon.ico to Img/app_icon.icns
    input_file = os.path.join(os.path.dirname(__file__), '..', '..', 'Img', 'app_icon.ico')
    output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'Img', 'app_icon.icns')
    
    image_convert_ico_to_icns(input_file, output_file)
