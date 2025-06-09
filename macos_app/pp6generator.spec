# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['pp6_cli_app.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/alex/Desktop/CMS/nodejs/pp6create/generate_presentation.py', '.'), ('/Users/alex/Desktop/CMS/nodejs/pp6create/generate_pp6_doc.py', '.'), ('/Users/alex/Desktop/CMS/nodejs/pp6create/generate_pp6_playlist.py', '.'), ('/Users/alex/Desktop/CMS/nodejs/pp6create/pptx_generator.py', '.'), ('/Users/alex/Desktop/CMS/nodejs/pp6create/pp6_xml_elements.py', '.'), ('/Users/alex/Desktop/CMS/nodejs/pp6create/pp6_color_utils.py', '.'), ('/Users/alex/Desktop/CMS/nodejs/pp6create/pp6_song_parser.py', '.')],
    hiddenimports=['PIL', 'PIL.Image', 'pptx', 'lxml', 'lxml.etree', 'dotenv', 'json', 'pathlib', 'argparse', 'uuid', 'base64', 'xml.etree.ElementTree', 're', 'datetime'],
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
    name='pp6generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons/app_icon.icns'],
)
