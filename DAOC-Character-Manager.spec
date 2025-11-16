# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Language', 'Language'),
        ('Img', 'Img'),
        ('Data', 'Data'),  # Include Data folder with realm ranks and other static game data
        ('Themes', 'Themes'),  # Include Themes folder with theme JSON files
    ],
    hiddenimports=[
        'UI.delegates',
        'UI.dialogs',
        'UI.debug_window',
        'Functions.ui_manager',
        'Functions.tree_manager',
        'Functions.character_actions_manager',
        'Functions.character_manager',
        'Functions.config_manager',
        'Functions.config_schema',        # Config v2 schema (NEW)
        'Functions.config_migration',     # Config v2 migration (NEW)
        'Functions.data_manager',
        'Functions.language_manager',
        'Functions.language_schema',      # Language v2 schema (NEW)
        'Functions.language_migration',   # Language v2 migration (NEW)
        'Functions.logging_manager',
        'Functions.migration_manager',
        'Functions.path_manager',
        'Functions.armor_manager',
        'Functions.theme_manager',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'Documentation',  # Exclude Documentation folder from build
        'Scripts',        # Exclude Scripts folder from build
        'Tools',          # Exclude Tools folder from build
        'Configuration',  # Exclude Configuration folder from build
        'Characters',     # Exclude Characters folder from build
        'Logs',           # Exclude Logs folder from build
        'Armures',        # Exclude Armures folder from build
        'pytest',         # Exclude test framework
        'unittest',       # Exclude unittest
        'test',           # Exclude any test modules
        'tkinter',        # Exclude tkinter if not needed
        '_tkinter',
        'matplotlib',     # Exclude matplotlib if not needed
        'PIL',            # Exclude Pillow if not needed
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DAOC Character Manager',
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
    icon='Img/app_icon.ico',  # Icône de l'application
)
