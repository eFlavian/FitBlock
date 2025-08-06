# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('icon.icns', '.')] if os.path.exists('icon.icns') else [],
    hiddenimports=[
        'Quartz',
        'Foundation', 
        'AppKit',
        'PyObjCTools',
        'objc',
        'objc._objc',
        'objc._pyobjc',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'PyObjCTools.AppHelper',
        'PyObjCTools.NibClassBuilder',
        'PyObjCTools.Conversion',
        'PyObjCTools.KeyValueCoding',
        'PyObjCTools.LazyProperty',
        'PyObjCTools.NSObjectController',
        'PyObjCTools.NSObjectControllerHelper',
        'PyObjCTools.NSObjectControllerHelper2',
        'PyObjCTools.NSObjectControllerHelper3',
        'PyObjCTools.NSObjectControllerHelper4',
        'PyObjCTools.NSObjectControllerHelper5',
        'PyObjCTools.NSObjectControllerHelper6',
        'PyObjCTools.NSObjectControllerHelper7',
        'PyObjCTools.NSObjectControllerHelper8',
        'PyObjCTools.NSObjectControllerHelper9',
        'PyObjCTools.NSObjectControllerHelper10',
    ],
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
    [],
    exclude_binaries=True,
    name='FitBlock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for final build
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns' if os.path.exists('icon.icns') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FitBlock',
)

app = BUNDLE(
    coll,
    name='FitBlock.app',
    icon='icon.icns' if os.path.exists('icon.icns') else None,
    bundle_identifier='com.fitblock.app',
    info_plist={
        'CFBundleName': 'FitBlock',
        'CFBundleDisplayName': 'FitBlock',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'FitBlock',
        'CFBundleIdentifier': 'com.fitblock.app',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'LSUIElement': True,  # This makes it a background app (no dock icon)
        'NSAppleEventsUsageDescription': 'FitBlock needs to control system settings for blocking functionality.',
        'CFBundleIconFile': 'icon.icns' if os.path.exists('icon.icns') else None,
    },
) 