#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script CLI pour construire la base de données items depuis des fichiers template
Wrapper pour items_parser.build_database_from_folder()
"""

import sys
from pathlib import Path
from .items_parser import build_database_from_folder

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_items_database.py <folder_path> [realm] [output_file]")
        print("\nExemples:")
        print("  python build_items_database.py Templates/Armures")
        print("  python build_items_database.py Templates/Armures Hibernia")
        print("  python build_items_database.py Templates/Armures All Data/items_database.json")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    realm = sys.argv[2] if len(sys.argv) > 2 else "All"
    output_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    build_database_from_folder(folder_path, output_file, realm)
