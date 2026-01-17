# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Language', 'Language'),
        ('Img', 'Img'),
        ('Data', 'Data'),
        ('Themes', 'Themes'),
    ],
    hiddenimports=[
        'UI.delegates', 'UI.dialogs', 'UI.debug_window', 'UI.ui_armor_resists_dialog',
        'Functions.ui_manager', 'Functions.tree_manager', 'Functions.character_actions_manager',
        'Functions.character_manager', 'Functions.config_manager', 'Functions.config_schema',
        'Functions.config_migration', 'Functions.data_manager', 'Functions.language_manager',
        'Functions.language_schema', 'Functions.language_migration', 'Functions.logging_manager',
        'Functions.migration_manager', 'Functions.path_manager', 'Functions.armor_manager',
        'Functions.armor_resists_manager', 'Functions.theme_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'Documentation', 'Scripts', 'Tools', 'Configuration', 'Characters', 
        'Logs', 'Armures', 'pytest', 'unittest', 'test', 'tkinter', '_tkinter', 
        'matplotlib', 'PIL'
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# DETECTION DE L'ICÔNE (Correction des Slashs)
if sys.platform == 'darwin':
    # On utilise des slashs / pour macOS
    icon_file = os.path.join('Img', 'app_icon.icns')
else:
    # os.path.join s'adapte automatiquement à l'OS
    icon_file = os.path.join('Img', 'app_icon.ico')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DaocCharacterManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,
)

# Optionnel : Pour macOS, cela crée le dossier .app proprement dit
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='DAOC Character Manager.app',
        icon=icon_file,
        bundle_identifier='com.daoc.charman',
    )