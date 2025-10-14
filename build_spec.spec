# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SSR JSON Editor

block_cipher = None

a = Analysis(
    ['json_editor.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'ijson'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SSR JSON Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file path here later
)

# macOS App Bundle
app = BUNDLE(
    exe,
    name='SSR JSON Editor.app',
    icon=None,  # You can add an .icns file path here later
    bundle_identifier='com.ssr.jsoneditor',
    info_plist={
        'NSHighResolutionCapable': 'True',
        'CFBundleName': 'SSR JSON Editor',
        'CFBundleDisplayName': 'SSR JSON Editor',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': 'Copyright © 2025',
    },
)
