# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Language', 'Language'),
        ('Img', 'Img'),
        ('Data', 'Data'),  # Include Data folder with realm ranks and other static game data
    ],
    hiddenimports=['UI.delegates', 'UI.dialogs', 'UI.debug_window'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'Documentation',  # Exclude documentation folder from build
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
)
