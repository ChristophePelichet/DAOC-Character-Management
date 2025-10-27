"""
Path Diagnostic Tool - Outil de diagnostic des chemins
Vérifie que tous les chemins fonctionnent correctement en mode dev et exe
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Functions.path_manager import get_base_path, get_resource_path
from Functions.character_manager import get_character_dir
from Functions.config_manager import get_config_dir
from Functions.logging_manager import get_log_dir, get_img_dir

def check_path(name, path, should_exist=None, is_resource=False):
    """Check a path and print diagnostic info"""
    exists = os.path.exists(path)
    path_type = "RESOURCE" if is_resource else "USER DATA"
    status = "✓" if exists else "✗"
    
    print(f"{status} [{path_type}] {name}:")
    print(f"  Path: {path}")
    print(f"  Exists: {exists}")
    
    if should_exist is not None and exists != should_exist:
        print(f"  ⚠️  WARNING: Expected exists={should_exist}, got {exists}")
    
    if exists and os.path.isdir(path):
        try:
            contents = os.listdir(path)[:5]  # First 5 items
            print(f"  Contents (first 5): {contents}")
        except PermissionError:
            print(f"  Contents: <Permission denied>")
    
    print()

def main():
    print("=" * 70)
    print("PATH DIAGNOSTIC TOOL")
    print("=" * 70)
    print()
    
    # Check if frozen
    is_frozen = getattr(sys, 'frozen', False)
    print(f"Running Mode: {'FROZEN (exe)' if is_frozen else 'DEVELOPMENT (script)'}")
    print(f"sys.frozen: {is_frozen}")
    
    if is_frozen:
        print(f"sys.executable: {sys.executable}")
        print(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'N/A')}")
    else:
        print(f"__file__: {__file__}")
    
    print()
    print("-" * 70)
    print("BASE PATHS")
    print("-" * 70)
    print()
    
    base_path = get_base_path()
    print(f"get_base_path(): {base_path}")
    print(f"  (Used for: User data - Characters, Configuration, Logs)")
    print()
    
    print("-" * 70)
    print("RESOURCE PATHS (Bundled with exe)")
    print("-" * 70)
    print()
    
    check_path("Images", get_img_dir(), should_exist=True, is_resource=True)
    check_path("Language", get_resource_path('Language'), should_exist=True, is_resource=True)
    check_path("Data", get_resource_path('Data'), should_exist=True, is_resource=True)
    
    # Check specific resources
    img_dir = get_img_dir()
    icons = ['icon-plus-50.png', 'reglage.png', 'colonnes.png', 'albion_logo.png']
    print("Specific Icons:")
    for icon in icons:
        icon_path = os.path.join(img_dir, icon)
        exists = "✓" if os.path.exists(icon_path) else "✗"
        print(f"  {exists} {icon}")
    print()
    
    lang_dir = get_resource_path('Language')
    langs = ['fr.json', 'en.json', 'de.json']
    print("Language Files:")
    for lang in langs:
        lang_path = os.path.join(lang_dir, lang)
        exists = "✓" if os.path.exists(lang_path) else "✗"
        print(f"  {exists} {lang}")
    print()
    
    data_dir = get_resource_path('Data')
    data_files = ['realm_ranks.json', 'README.md']
    print("Data Files:")
    for data_file in data_files:
        data_path = os.path.join(data_dir, data_file)
        exists = "✓" if os.path.exists(data_path) else "✗"
        print(f"  {exists} {data_file}")
    print()
    
    print("-" * 70)
    print("USER DATA PATHS (Created next to exe)")
    print("-" * 70)
    print()
    
    check_path("Characters", get_character_dir(), should_exist=False, is_resource=False)
    check_path("Configuration", get_config_dir(), should_exist=False, is_resource=False)
    check_path("Logs", get_log_dir(), should_exist=False, is_resource=False)
    
    print("-" * 70)
    print("SUMMARY")
    print("-" * 70)
    print()
    
    # Count issues
    issues = []
    
    # Check resources
    if not os.path.exists(get_img_dir()):
        issues.append("❌ Img folder not found")
    if not os.path.exists(get_resource_path('Language')):
        issues.append("❌ Language folder not found")
    if not os.path.exists(get_resource_path('Data')):
        issues.append("❌ Data folder not found")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print()
        print("⚠️  If running as exe, make sure .spec includes:")
        print("     datas=[('Language', 'Language'), ('Img', 'Img'), ('Data', 'Data')]")
    else:
        print("✓ All critical paths OK")
        print()
        print("Note: User data folders (Characters, Configuration, Logs)")
        print("      will be created automatically on first use.")
    
    print()
    print("=" * 70)

if __name__ == '__main__':
    main()
