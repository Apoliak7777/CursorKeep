# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# Collect full packages for reliable tray + PIL + GUI in onefile
pystray_datas, pystray_bins, pystray_hids = collect_all('pystray')
pil_datas, pil_bins, pil_hids = collect_all('PIL')

a = Analysis(
    ['cursorkeep.py'],
    pathex=[],
    binaries=pystray_bins + pil_bins,
    datas=pystray_datas + pil_datas + [('CursorKeep.ico', '.')],
    hiddenimports=[
        'pystray', 'pystray._win32',
        'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL._imaging',
        'pyautogui', 'pyautogui._pyautogui_win',
        'keyboard', 'keyboard._winkeyboard',
    ] + pystray_hids + pil_hids,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='CursorKeep',
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
    icon=['CursorKeep.ico'],
)
